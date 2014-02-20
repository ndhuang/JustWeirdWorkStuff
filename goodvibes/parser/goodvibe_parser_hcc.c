#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#include <stdint.h>

#define BUFFER_LENGTH 4096
#define tick_period 5.12e-6

// 0xc0=0b1100 0000, 0xfc=0b1111 1100
#define tickID   0xc0          // 0b1100 0000      
#define tickRolloverID 0x60    // 0b0110 0000  
#define tempID   0x40          // 0b0100 0000
#define accelXID 0x84          // 0b1000 0100
#define accelYID 0x88          // 0b1000 1000
#define accelZID 0x8c          // 0b1000 1100
#define micAllID 0x00          // 0b0000 0000
#define mic1ID   0b00000100
#define mic2ID   0b00001000
#define mic3ID   0b00001100
#define mic4ID   0b00010000
#define mic5ID   0b00010100
#define mic6ID   0b00011000
#define mic7ID   0b00011100
#define mic8ID   0b00100000
#define mic9ID   0b00100100
#define mic10ID  0b00101000


void usage()
{
  printf("goodvibe_parser.c: Parse packets dumped from ");
  printf("McGill Good Vibrations Monitoring circuit board.\n");
  printf("\n");
  printf("usage: limpet [ARGUMENTS]...\n");
  printf("\n");
  printf("Arguments are the following:\n");
  printf("	[-p|--port]	selects a UDP port (default 48010)\n");
  printf("	[-o|--oname]	prefix to be used for datafiles.\n");
  printf("	[-s|--screen]	also dumps to screen (stdout).\n");
  printf("      [-f|---file]    dumps screen data to file instead.\n");
  printf("	[-h|--help]	the message you're viewing now.\n");
  printf("\n");
}

void byte_to_string( char* s, uint8_t b)
{
  // This routine just takes a byte input, like 0x11 and converts it to 
  //    a string with its bit representation, "0b00010001".
  int i;
  s[0] = '0';
  s[1] = 'b';
  for (i=0; i<8; i++) {
    if ( b & (0x01<<i) ) { s[9-i]='1';
    } else { s[9-i]='0'; }
  }
  s[10]=0;
}

int main(int argc, char **argv)
{
  
  FILE *myscreen = stdout;
  FILE *file_ticks_mic = 0;
  FILE *file_secs_mic = 0;
  FILE *file_ticks_accel = 0;
  FILE *file_secs_accel = 0;
  FILE *file_mic = 0;
  FILE *file_accel = 0;
  FILE *file_temp = 0;
  char filenamePrefix[100];
  char filenameTmp[200];

  int sock = -1;
  int port = 48010;
  struct sockaddr_in dst;
  struct sockaddr_in src;
  socklen_t src_len;

  int c;
  int n;
  int buf_occ;  // size of buffer for incoming udp data
  char *buf;    // buffer for incoming udp data

  char hbitstring[11];
  char lbitstring[11];
  uint8_t hbyte = 0;
  uint8_t lbyte = 0;
  uint16_t adc;
  uint16_t adc_accelX;
  uint16_t adc_accelY;
  uint16_t adc_accelZ;
  uint16_t tick;
  uint16_t last_tick;
  float tick_us = 0.;
  float last_tick_us = 0.;
  double tick_seconds = 0.;
  float tick_seconds_tmp = 0.;
  int64_t total_ticks = 0;
  int32_t total_ticks_tmp = 0;
  int32_t tick_rollover_counter = 0;
  double last_frame_seconds = 0.;
  int64_t frame_total_ticks = 0;
  double frame_seconds =0.;
  #define TRUE 1
  #define FALSE 0
  uint8_t useScreen = FALSE;
  int pktnum = 0;

  // ------------- Parse command-line arguments ---------------
  strcpy(filenamePrefix,"data");
  while (1) {
    int option_index = 0;
    static struct option long_options[] = {
      {"help", 0, 0, 'h'},
	  {"screen", 0, 0, 's'},
      {"file", 1, 0, 'f'},
      {"port", 1, 0, 'p'},
      {"oname", 1, 0, 'o'},
      {0, 0, 0, 0}
    };

    c = getopt_long(argc, argv, "hp:o:f:s", long_options,
		    &option_index);
    if (c == -1)
      break;

    switch (c) {
    case 's':
      useScreen = TRUE;
      break;
    case 'p':
      port = atoi(optarg);
      break;
    case 'o':
      strcpy(filenamePrefix,optarg);
      printf("using file prefex %s", filenamePrefix );
      break;
    case 'f':
      if (!(myscreen = fopen(optarg, "w"))) {
	perror("fopen");
	exit(-1);
      }
      break;  
    case 'h':
    default:
      usage();
      exit(-1);
      break;
    }
  }
  if (optind < argc) {
    usage();
    exit(-1);
  }

  // ---------------- Open files to write output to --------------
  //md: need to add filename prefix instead of out.

  strcpy(filenameTmp, filenamePrefix);
  if (!(file_ticks_mic = fopen( strcat(filenameTmp,"/ticks_mic"), "a") )) {
    perror("fopen error on ticks");
    exit(-1);
  }
  //strcpy(filenameTmp, filenamePrefix);
  //if (!(file_secs_mic = fopen( strcat(filenameTmp,"/seconds_mic"), "a") )) {
  //  perror("fopen error on secs");
  //  exit(-1);
  //}
  strcpy(filenameTmp, filenamePrefix);
  if (!(file_ticks_accel = fopen( strcat(filenameTmp,"/ticks_accel"), "a") )) {
    perror("fopen error on ticks");
    exit(-1);
  }
  //strcpy(filenameTmp, filenamePrefix);
  //if (!(file_secs_accel = fopen( strcat(filenameTmp,"/seconds_accel"), "a") )) {
  //  perror("fopen error on secs");
  //  exit(-1);
  //}
  strcpy(filenameTmp, filenamePrefix);
  if (!(file_mic = fopen( strcat(filenameTmp,"/mic"), "a") )) {
    perror("fopen error on mic");
    exit(-1);
  }
  strcpy(filenameTmp, filenamePrefix);
  if (!(file_accel = fopen( strcat(filenameTmp,"/accel"), "a"))) {
    perror("fopen error on accel");
    exit(-1);
  }
  strcpy(filenameTmp, filenamePrefix);
  if (!(file_temp = fopen( strcat(filenameTmp,"/Temp"), "a"))) {
    perror("fopen error on temp");
    exit(-1);
  }

  // setup UDP socket
  sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  if (sock < 0) {
    perror("socket");
    exit(-1);
  }

  memset(&dst, 0, sizeof(dst));
  dst.sin_family = AF_INET;
  dst.sin_addr.s_addr = htonl(INADDR_ANY);
  dst.sin_port = htons(port);
  
  /* bind to receive address */
  if (bind(sock, (struct sockaddr *)&dst, sizeof(dst)) < 0) {
    perror("bind");
    exit(-1);
  }

  /* Allocate receive buffer */
  buf = (char *)malloc(BUFFER_LENGTH);
  if (!buf) {
    fprintf(stderr, "Unable to allocate data buffer!");
    exit(-1);
  }
  
  // ------------ Write headers on all files ------------------------
  if (useScreen) {
    fprintf(myscreen, "Source IP\tPktnum\tOffset\thigh byte\tlow btye\n");
    fflush(myscreen);
  }
	
  // ------------ infinite loop receiving UDP packets ------------------
  while (1) {
    src_len = sizeof(src);
    buf_occ = recvfrom(sock, buf, BUFFER_LENGTH, 0, 
		       (struct sockaddr *)&src, &src_len);
    if(!buf_occ || buf_occ==-1) {
      perror("recvfrom");
      exit(-1);
    }
    pktnum++;
    adc_accelX =0;
    adc_accelY =0;
    adc_accelZ =0;

    // ------------ loop over UDP message byte by byte ------------------
    for(n=0; n<buf_occ; n+=2) {
      hbyte = buf[n];
      lbyte = buf[n+1];
      byte_to_string(hbitstring, hbyte);
      byte_to_string(lbitstring, lbyte);

      if (useScreen) {
    	fprintf(myscreen,"%s  %i  %i\t%03u=%s\t%03u=%s \n",
	       inet_ntoa(((struct sockaddr_in *)&src)->sin_addr), //ip
	       pktnum, // packet number
	       n>>1,   // entry offset in packet (half the byte offset)
	       hbyte, hbitstring, lbyte, lbitstring );
	    fflush(myscreen);
      }

      if ( (hbyte&0xc0) == tickID){
	last_tick = tick;
	tick = (hbyte&0x3f)*256 + lbyte;
	if ( ( (int32_t)tick-(int32_t)last_tick ) <0 ) tick_rollover_counter++;
	total_ticks = ((int64_t)tick) + 16384*((int64_t)tick_rollover_counter);
	tick_seconds =  ((double)total_ticks) * tick_period;

	last_tick_us = tick_us;
	tick_us = ((float)tick) * tick_period * 1.e6;
	// for reasons I do not understand, fprintf cannot handle 64 bit
	//   numbers. This means to print a number we hae to cast it as 32 bit.
	if (useScreen) {
	  fprintf(myscreen,
	       "\t\t %03u=%s\t%03u=%s\t tick=%u=%f us, dt=%f, tt=%d=%18.6f\n",
		  hbyte, hbitstring, lbyte, lbitstring,
		  tick, tick_us, tick_us-last_tick_us,
		  (int32_t)total_ticks, (float)tick_seconds );
	  fflush(myscreen);
	}
      } else if ( hbyte == tickRolloverID ){
	last_frame_seconds = frame_seconds;
	frame_total_ticks = ((int64_t)tick) + 16384*((int64_t)lbyte);
	frame_seconds = ((double)frame_total_ticks) * tick_period;
	if (useScreen) {
	  fprintf(myscreen,
		  "FRAME total ticks: =%u=%f sec, dt=%f sec --\n",
		  (int32_t)frame_total_ticks, (float)frame_seconds, 
		  (float)(frame_seconds-last_frame_seconds));
	  fflush(myscreen);
	}
 
      } else if ( (hbyte&0xc0) == micAllID){
	adc = (hbyte&0x03)*256 + lbyte;
	// microphone data
	fwrite(&adc, sizeof(uint16_t), 1, file_mic);
	fflush(file_mic);

	total_ticks_tmp = (int32_t)total_ticks;
	fwrite(&total_ticks_tmp, sizeof(int32_t), 1, file_ticks_mic); 
	fflush(file_ticks_mic);
	//tick_seconds_tmp = (float)tick_seconds;
	//fwrite(&tick_seconds_tmp, sizeof(float), 1, file_secs_mic);
	//fflush(file_secs_mic);
      } else if ( (hbyte&0xfc) == accelXID){
	adc_accelX = (hbyte&0x03)*256 + lbyte;
      } else if ( (hbyte&0xfc) == accelYID){
	adc_accelY = (hbyte&0x03)*256 + lbyte;
      } else if ( (hbyte&0xfc) == accelZID){
	adc_accelZ = (hbyte&0x03)*256 + lbyte;
	// accelerometer z data -- note x/y fields seem to be empty right now
	fwrite(&adc_accelZ, sizeof(uint16_t), 1, file_accel);
	fflush(file_accel);

	total_ticks_tmp = (int32_t)total_ticks;
	fwrite(&total_ticks_tmp, sizeof(int32_t), 1, file_ticks_accel); 
	fflush(file_ticks_accel);
	//tick_seconds_tmp = (float)tick_seconds;
	//fwrite(&tick_seconds_tmp, sizeof(float), 1, file_secs_accel);
	//fflush(file_secs_accel);
      } else if ( (hbyte&0xfc) == tempID){
	adc = (hbyte&0x03)*256 + lbyte;
	// temp data
	fwrite(&adc, sizeof(uint16_t), 1, file_temp);
	fflush(file_temp);
      }

    }
  }

  exit(-1);
}
