import time
import random
import threading
import queue

import logging
# create logger
logger = logging.getLogger(__name__)

import rpi_ws281x

# Gamma correction makes the colours perceived correctly.
gamma8 = [
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255]


class LUMapPixel:

    def __init__(self, pixel_num, station, line):
        self.pixel_num = pixel_num
        self.station = station
        self.line = line
        self.debug_out()

    def debug_out(self):
        logger.debug("{} pixel {} {}, ".format(self.pixel_num, self.line, self.station))



stations = [
LUMapPixel(0, 'Amersham', 'Met'),
LUMapPixel(1, 'Chalfort and Latimer', 'Met'),
LUMapPixel(2,'Rickmansworth' , 'Met'),
LUMapPixel(3, 'Northwood', 'Met'),
LUMapPixel(4, 'Pinner', 'Met'),
LUMapPixel(5, 'Harrow-on-the-hill', 'Met'),
LUMapPixel(6, 'Northwick Park', 'Met'),
LUMapPixel(7, 'Preston Road', 'Met'),
LUMapPixel(8, 'Wembley Park', 'Met'),
LUMapPixel(9, 'Stanmore', 'Jub'),
LUMapPixel(10, 'Kingsbury', 'Jub'),
LUMapPixel(11, 'Wembley Park', 'Jub'),
LUMapPixel(12, 'Kilburn', 'Jub'),
LUMapPixel(13, 'Finchley Road', 'Met'),
LUMapPixel(14, 'Finchley Road', 'Jub'),
LUMapPixel(15, 'Swiss Cottage', 'Jub'),
LUMapPixel(16, 'Baker Street', 'Met'),
LUMapPixel(16, 'Baker Street', 'Circle'),
LUMapPixel(16, 'Baker Street', 'H&C'),
LUMapPixel(17, 'Euston Square', 'H&C'),
LUMapPixel(17, 'Euston Square', 'Met'),
LUMapPixel(17, 'Euston Square', 'Circle'),
LUMapPixel(18, 'Kings Cross', 'H&C'),
LUMapPixel(18, 'Kings Cross', 'Met'),
LUMapPixel(18, 'Kings Cross', 'Circle'),
LUMapPixel(19, 'Barbican', 'H&C'),
LUMapPixel(19, 'Barbican', 'Met'),
LUMapPixel(19, 'Barbican', 'Circle'),
LUMapPixel(20, 'Moorgate', 'H&C'),
LUMapPixel(20, 'Moorgate', 'Met'),
LUMapPixel(20, 'Moorgate', 'Circle'),
LUMapPixel(21, 'Liverpool Street', 'H&C'),
LUMapPixel(21, 'Liverpool Street', 'Met'),
LUMapPixel(21, 'Liverpool Street', 'Circle'),
LUMapPixel(22, 'Tower Hill', 'District'),
LUMapPixel(22, 'Tower Hill', 'Circle'),
LUMapPixel(23, 'Aldgate East', 'H&C'),
LUMapPixel(23, 'Aldgate East', 'District'),
LUMapPixel(33, 'Stepney Green', 'H&C'),
LUMapPixel(33, 'Stepney Green', 'District'),
LUMapPixel(24, 'Mile End', 'H&C'),
LUMapPixel(24, 'Mile End', 'District'),
LUMapPixel(25, 'West Ham', 'H&C'),
LUMapPixel(25, 'West Ham', 'District'),
LUMapPixel(26, 'East Ham', 'H&C'),
LUMapPixel(26, 'East Ham', 'District'),
LUMapPixel(28, 'Upminster', 'District'),
LUMapPixel(29, 'Elm Park', 'District'),
LUMapPixel(30, 'Upney', 'District'),
LUMapPixel(31, 'Plaistow', 'District'),
LUMapPixel(32, 'Bromley-by-Bow', 'District'),
LUMapPixel(34, 'Aldgate', 'Met'),
LUMapPixel(34, 'Aldgate', 'Circle'),
LUMapPixel(35, 'Monument', 'Circle'),
LUMapPixel(35, 'Monument', 'District'),
LUMapPixel(38, 'Blackfriars', 'Circle'),
LUMapPixel(38, 'Blackfriars', 'District'),
LUMapPixel(36, 'Temple', 'Circle'),
LUMapPixel(36, 'Temple', 'District'),
LUMapPixel(37, 'Cannon Street', 'Circle'),
LUMapPixel(37, 'Cannon Street', 'District'),
LUMapPixel(39, 'Embankment', 'Circle'),
LUMapPixel(39, 'Embankment', 'District'),
LUMapPixel(41, 'Westminster', 'Circle'),
LUMapPixel(41, 'Westminster', 'District'),
#LUMapPixel(42, 'Victoria', 'Circle'),
#LUMapPixel(42, 'Victoria', 'District'),
LUMapPixel(42, 'South Kensington', 'Circle'),
LUMapPixel(42, 'South Kensington', 'District'),
LUMapPixel(43, 'Putney Bridge', 'District'),
LUMapPixel(44, 'Wimbledon', 'District'),
LUMapPixel(45, 'Wimbledon Park', 'District'),
LUMapPixel(46, 'West Brompton', 'District'),
LUMapPixel(47, 'Richmond', 'District'),
LUMapPixel(48, 'Ealing Broadway', 'District'),
LUMapPixel(49, 'Acton Town', 'District'),
LUMapPixel(50, 'Turnham Green', 'District'),
LUMapPixel(51, 'Kew Garden', 'District'),
LUMapPixel(52, 'Ealing Common', 'District'),
LUMapPixel(53, 'Gunnersby', 'District'),
LUMapPixel(54, 'Hammersmith', 'H&C'),
LUMapPixel(54, 'Hammersmith', 'Circle'),
LUMapPixel(55, 'Ladbroke Grove', 'H&C'),
LUMapPixel(55, 'Ladbroke Grove', 'Circle'),
LUMapPixel(56, 'High Street Kensington', 'Circle'),
LUMapPixel(56, 'High Street Kensington', 'District'),
LUMapPixel(57, 'Earls Court', 'District'),
LUMapPixel(58, 'Notting Hill Gate', 'Circle'),
LUMapPixel(58, 'Notting Hill Gate', 'District'),
LUMapPixel(59, 'Wood Lane', 'H&C'),
LUMapPixel(59, 'Wood Lane', 'Circle'),
LUMapPixel(60, 'Paddington', 'H&C'),
LUMapPixel(60, 'Paddington', 'Circle'),
LUMapPixel(61, 'Paddington', 'Circle'),
LUMapPixel(61, 'Paddington', 'District'),
LUMapPixel(62, 'Edgware Road', 'Circle'),
LUMapPixel(62, 'Edgware Road', 'H&C'),
LUMapPixel(62, 'Edgware Road', 'District'),
LUMapPixel(63, 'Royal Oak', 'H&C'),
LUMapPixel(63, 'Royal Oak', 'Circle'),

]

line_colours = {
'District':(51, 51, 0),
'Circle':(75, 75, 35),
'H&C':(50, 85, 85),
'Jub': (75, 75, 75),
'Met': (0, 102, 51)
}

# Class to  control the LED Strip based on the tweets.
class LedStripControl(threading.Thread):

    # Set up the strip with the passed parameters.  The Gamma correction is done by the library, so it gete passed in.
    def __init__(self, led_count, led_pin, type = None):

        # Init the threading
        threading.Thread.__init__(self)

        self.strip = rpi_ws281x.PixelStrip(led_count, led_pin, gamma=gamma8, strip_type= type)

        # Intialize the library (must be called once before other functions).
        self.strip.begin()
        self.incoming_queue = queue.Queue()

    def set_same_colour(self, colour, count= None):

        if (count == None):
            count = self.strip.numPixels()

        print(count)
        for i in range(count):
            self.strip.setPixelColor(i, rpi_ws281x.Color(*colour))
        self.strip.show()

    def station_query(self, pixel):
        for item in stations:
            if item.pixel_num == pixel:
                print(item.pixel_num, item.line, item.station)


    '''
    # Set the strip colours according to the passed in list.  Set Twinkle Ratio to 0 if you don't want any twinkle.
    def set_strip_colours(self, tweet_list, twinkle_ratio = 0.25, tweeter_filter = None):
        for pixel in range (0, len(tweet_list)):
            #print(colour_list[pixel])
            #print(pixel, tweet_list[pixel].name)

            twinkle_on_off = random.random()
            #print(twinkle_on_off)

            # If no filter, the show all pixels.
            if tweeter_filter is None:
                if float(twinkle_on_off) < float(twinkle_ratio):
                    self.strip.setPixelColor(pixel, rpi_ws281x.Color(0, 0, 0))
                else:
                    self.strip.setPixelColor(pixel, rpi_ws281x.Color(*tweet_list[pixel].colour))

            # Check against the filter
            elif tweet_list[pixel].id is tweeter_filter.id:
                self.strip.setPixelColor(pixel, rpi_ws281x.Color(*tweet_list[pixel].colour))

            # Otherwise set to off.
            else:
                self.strip.setPixelColor(pixel, rpi_ws281x.Color(0,0,0))


            #self.strip.setPixelColor(pixel, rpi_ws281x.Color(*tweet_list[pixel].colour))

        # The below commented out bit sets the rest to dark.
        for pixel in range(len(tweet_list), self.strip.numPixels()):
           self.strip.setPixelColor(pixel, rpi_ws281x.Color(0, 0, 0))

        self.strip.show()
    '''

    # Clears al the pixels.
    def pixel_clear(self):
        # Clear all the pixels
        for i in range(0, self.strip.numPixels()):  # Green Red Blue
            self.strip.setPixelColor(i, rpi_ws281x.Color(0, 0, 0))

        self.strip.show()

    def pixel_travel(self):
        for i in range(0, 64):
            self.strip.setPixelColor(i, rpi_ws281x.Color(85, 85, 0))
            self.strip.show()
            print(i)
            self.station_query(i)
            time.sleep(1)
            self.strip.setPixelColor(i, rpi_ws281x.Color(0, 0, 0))
            self.strip.show()

    def draw_line(self, line):
        for i in range(100):
            self.strip.setPixelColor(i, rpi_ws281x.Color(0, 0, 0))
        for station in stations:
            print(station.pixel_num, station.line, station.station)
            if station.line == line:
                print("match line ", station.line)
                self.strip.setPixelColor(station.pixel_num, rpi_ws281x.Color(*line_colours[line]))
        self.strip.show()

    def pixel_jump(self):
        for i in range(100):
            self.strip.setPixelColor(i, rpi_ws281x.Color(85, 85, 0))
            self.strip.show()
            time.sleep(0.3 - i * 0.003)
            self.strip.setPixelColor(i, rpi_ws281x.Color(50, 0, 50))
            self.strip.show()

    def run(self):
        try:
            pixels =[]

            while True:
                # Get the latest commanded pixels from the queue
                while not self.incoming_queue.empty():
                    pixels = self.incoming_queue.get_nowait()
                    logger.debug("Colour of pixel 0 {}".format(pixels[0]))
                    self.pixel_clear()

                # logger.debug("LED Strip {}".format(len(pixels)))

                # Get number of pixels to display - max is number of pixels.
                pixels_to_display = min(len(pixels), self.strip.numPixels())

                #logger.debug("Pixels to display {}".format(pixels_to_display))

                #self.set_same_colour()

                #time.sleep(3)

                # self.pixel_clear()

                for i in range(0, pixels_to_display):
                    # print(colour_list[pixel])
                    # logger.debug("{} {}".format(i, pixels[i]))
                    self.strip.setPixelColor(i, pixels[i])
                    # self.strip.show()
                    #time.sleep(0.1)

                    '''
                    twinkle_on_off = random.random()
                    # print(twinkle_on_off)

                    # If no filter, the show all pixels.
                    if tweeter_filter is None:
                        if float(twinkle_on_off) < float(twinkle_ratio):
                            self.strip.setPixelColor(pixel, rpi_ws281x.Color(0, 0, 0))
                        else:
                            self.strip.setPixelColor(pixeli, rpi_ws281x.Color(*tweet_list[pixel].colour))

                    # Check against the filter
                    elif tweet_list[pixel].id is tweeter_filter.id:
                        self.strip.setPixelColor(pixel, rpi_ws281x.Color(*tweet_list[pixel].colour))

                    # Otherwise set to off.
                    else:
                        self.strip.setPixelColor(pixel, rpi_ws281x.Color(0, 0, 0))

                    # self.strip.setPixelColor(pixel, rpi_ws281x.Color(*tweet_list[pixel].colour))
                '''
                # The below commented out bit sets the rest to dark.
                for i in range(pixels_to_display, self.strip.numPixels()):
                    self.strip.setPixelColor(i, rpi_ws281x.Color(0, 0, 0))
                    #logger.debug(i)

                self.strip.show()

                #logger.debug("strip showed")
                time.sleep(0.1)

        except KeyboardInterrupt:
            logger.exception("Keyboard interrupt")

        except:
            raise

        finally:
            # Todo: Can't get back to 0 RPM when shutdown by Ctrl-C
            logger.error("finally")

if __name__ == "__main__":

    # LED strip configuration:
    LED_COUNT      = 100      # Number of LED pixels.
    LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
    #LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
    #LED_DMA        = 10       # DMA channel to use for generating signal (try 5)
    #LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
    #LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

    led_strip = LedStripControl(LED_COUNT, LED_PIN, type = rpi_ws281x.SK6812_STRIP)

    colours = [(75,0,0) , (0,75,0), (0, 0, 75), (75, 0, 75), (75, 75, 75), (100, 100, 100)]

    while True:
        led_strip.pixel_clear()
        print("pixel Clear")
        time.sleep(0.1)

        #tweet_strip.set_strip_colours(colours)
        #for colour in colours:
        #    print(colour)
        #    led_strip.set_same_colour(colour)
        #    time.sleep(1)

        led_strip.pixel_clear()
        #led_strip.pixel_jump()

        #for i in range (100, 255):
        colour = [70, 70, 70]
        #    print(colour)
        #led_strip.set_same_colour(colour, count=100)

        #led_strip.pixel_travel()
        led_strip.draw_line('District')
        time.sleep(2)

        led_strip.draw_line('Circle')
        time.sleep(2)

        led_strip.draw_line('H&C')
        time.sleep(2)

        led_strip.draw_line('Met')
        time.sleep(2)

        led_strip.draw_line('Jub')
        time.sleep(2)



        #time.sleep(5)