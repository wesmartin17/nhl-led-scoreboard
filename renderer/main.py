from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from utils import center_text, time_countdown
from calendar import month_abbr
from renderer.screen_config import screenConfig
import time
import debug

class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.screen_config = screenConfig("32x32_config")
        self.canvas = matrix.CreateFrameCanvas()
        self.width = 32
        self.height = 32

        # Create a new data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # Load the fonts
        self.font = ImageFont.truetype("fonts/score_large.otf", 12)
        self.font_mini = ImageFont.truetype("fonts/00 Starmap Truetype.ttf", 8)
        self.font_abbvr = ImageFont.truetype("fonts/04B_03__.TTF", 8)
        self.font_score = ImageFont.truetype("fonts/04b_25__.ttf", 12)

    def render(self):
        # loop through the different state.
        while True:
            self.data.get_current_date()
            self.data.refresh_fav_team_status()
            # Fav team game day
            if self.data.fav_team_game_today:
                debug.info('Game day State')
                self.__render_game()
            # Fav team off day
            else:
                debug.info('Off day State')
                self.__render_off_day()

    def __render_game(self):
        if self.data.fav_team_game_today == 1:
            debug.info('Scheduled State')
            self._draw_pregame()
            time.sleep(0.3)
        elif self.data.fav_team_game_today == 2:
            debug.info('Pre-Game State')
            self._draw_game()
            time.sleep(0.3)
        elif (self.data.fav_team_game_today == 3) or (self.data.fav_team_game_today == 4):
            debug.info('Live State')
            # Draw the current game
            self._draw_game()
        elif (self.data.fav_team_game_today == 5) or (self.data.fav_team_game_today == 6) or (self.data.fav_team_game_today == 7):
            debug.info('Final State')
            self._draw_post_game()
            #sleep an hour
            time.sleep(3600)
        debug.info('ping render_game')

    def __render_off_day(self):

        debug.info('ping_day_off')
        self._draw_off_day()
        time.sleep(21600) #sleep 6 hours

    def _draw_pregame(self):

        if self.data.get_schedule() != 0:

            overview = self.data.schedule
            home_abvr = self.data.get_teams_info[overview['home_team_id']]['abbreviation']
            away_abvr = self.data.get_teams_info[overview['away_team_id']]['abbreviation']
            
            home_color_primary = str(self.screen_config.team_colors[str(overview['home_team_id'])]["primary"])
            home_color_secondary = str(self.screen_config.team_colors[str(overview['home_team_id'])]["secondary"])
            home_color_text = str(self.screen_config.team_colors[str(overview['home_team_id'])]["text"])

            away_color_primary = str(self.screen_config.team_colors[str(overview['away_team_id'])]["primary"])
            away_color_secondary = str(self.screen_config.team_colors[str(overview['away_team_id'])]["secondary"])
            away_color_text = str(self.screen_config.team_colors[str(overview['away_team_id'])]["text"])

            # Save when the game start
            game_time = overview['game_time']

            # Home team render
            self.draw.rectangle(((0, 0), (15, 7)), fill= home_color_primary)
            self.draw.rectangle(((0,7),(15, 8)), fill = home_color_secondary)
            self.draw.text((1, 0), home_abvr,font=self.font_abbvr, fill= home_color_text)

            # Visitor team render
            self.draw.rectangle(((16, 0), (32, 7)), fill= away_color_primary)
            self.draw.rectangle(((16,7),(32, 8)), fill = away_color_secondary)
            self.draw.text((center_text(self.font_abbvr.getsize(away_abvr)[0], 24), 0), away_abvr,font=self.font_abbvr, fill=away_color_text)

            # Center the game time on screen.
            game_time_pos = center_text(self.font_mini.getsize(game_time)[0], 12)

            # Get current hours/minutes/seconds until the game starts
            game_time_str = time_countdown(game_time)

            # Center the game time on screen.
            game_time_pos = center_text(self.font.getsize(game_time_str)[0], 18)
            
            # Draw the game time on the screen
            self.draw.text((game_time_pos,17), game_time_str, fill=('orange'), font=self.font_abbvr)

            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)

            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
        else:
            #(Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(60)  # sleep for 1 min
            # Refresh canvas
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

    def _draw_game(self):

        self.data.refresh_overview()
        overview = self.data.overview
        home_color_primary = str(self.screen_config.team_colors[str(overview['home_team_id'])]["primary"])
        home_color_secondary = str(self.screen_config.team_colors[str(overview['home_team_id'])]["secondary"])
        home_color_text = str(self.screen_config.team_colors[str(overview['home_team_id'])]["text"])

        away_color_primary = str(self.screen_config.team_colors[str(overview['away_team_id'])]["primary"])
        away_color_secondary = str(self.screen_config.team_colors[str(overview['away_team_id'])]["secondary"])
        away_color_text = str(self.screen_config.team_colors[str(overview['away_team_id'])]["text"])

        home_abvr = self.data.get_teams_info[overview['home_team_id']]['abbreviation']
        away_abvr = self.data.get_teams_info[overview['away_team_id']]['abbreviation']
        
        home_score = overview['home_score']
        away_score = overview['away_score']

        while True:

            # Refresh the data
            if self.data.needs_refresh:
                debug.info('Refresh game overview')
                self.data.refresh_overview()
                self.data.needs_refresh = False

            if self.data.overview != 0:
                overview = self.data.overview

                if overview['home_score'] > home_score or overview['away_score'] > away_score:
                   self._draw_goal()
                
                # Home team render
                self.draw.rectangle(((0, 0), (15, 7)), fill= home_color_primary)
                self.draw.rectangle(((0,7),(15, 8)), fill = home_color_secondary)
                self.draw.text((center_text(self.font_abbvr.getsize(home_abvr)[0], 9),0), home_abvr,font=self.font_abbvr, fill= home_color_text)

                # Visitor team render
                self.draw.rectangle(((16, 0), (32, 7)), fill= away_color_primary)
                self.draw.rectangle(((16,7),(32, 8)), fill = away_color_secondary)
                self.draw.text((center_text(self.font_abbvr.getsize(away_abvr)[0], 24), 0), away_abvr,font=self.font_abbvr, fill=away_color_text)

                # Center the scores
                home_score_pos = center_text(self.font.getsize(str(home_score))[0], 8)
                away_score_pos = center_text(self.font.getsize(str(away_score))[0], 24)

                self.draw.text((home_score_pos, 7), str(overview['home_score']),font=self.font_score, fill='orange')
                self.draw.text((away_score_pos, 7), str(overview['away_score']),font=self.font_score, fill='orange')

                period_str = overview['period']
                time_str = overview['time']
                
                # In Intermission
                is_intermission = False
                if overview['is_intermission']:
                    is_intermission = True
                    period_str = "{} INT".format(period_str)
                    int_time_remaining = int(overview['intermission_time_rem'])
                    minutes = (int_time_remaining - int_time_remaining % 60) / 60
                    seconds = int_time_remaining % 60
                    time_str = "{}:{}".format(str(minutes),str(seconds).zfill(2))

                # Set the position of the information on screen.
                time_pos = center_text(self.font_abbvr.getsize(time_str)[0], 16)
                period_pos = center_text(self.font_abbvr.getsize(period_str)[0], 16)
                
                self.draw.text((time_pos, 19), time_str, fill='orange', font=self.font_abbvr)
                self.draw.text((period_pos, 26), period_str, fill='orange', font=self.font_abbvr)
                
                # Put the data on the canvas
                self.canvas.SetImage(self.image, 0, 0)

                # Load the canvas on screen.
                self.canvas = self.matrix.SwapOnVSync(self.canvas)

                # Refresh the Data image.
                self.image = Image.new('RGB', (self.width, self.height))
                self.draw = ImageDraw.Draw(self.image)


                # Check if the game is over
                if overview['game_status'] == 6 or overview['game_status'] == 7:
                    debug.info('GAME OVER')
                    break

                # Save the scores.
                away_score = overview['away_score']
                home_score = overview['home_score']

                self.data.needs_refresh = True

                if is_intermission:
                    time.sleep(20)
                else:
                    time.sleep(20)
            else:
                # (Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
                self.draw.line((0, 0) + (self.width, 0), fill=128)
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                time.sleep(60)  # sleep for 1 min

    def _draw_post_game(self):
        self.data.refresh_overview()
        if self.data.overview != 0:
            overview = self.data.overview

            # Prepare the data
            game_date = '{} {}'.format(month_abbr[self.data.month], self.data.day)
            score = '{}-{}'.format(overview['away_score'], overview['home_score'])
            period = overview['period']
            time_period = overview['time']

            # Set the position of the information on screen.
            game_date_pos = center_text(self.font_mini.getsize(game_date)[0], 16)
            time_period_pos = center_text(self.font_mini.getsize(time_period)[0], 16)
            score_position = center_text(self.font_abb.getsize(score)[0], 32)

            # Draw the text on the Data image.
            self.draw.multiline_text((game_date_pos, -1), game_date, fill=(255, 255, 255), font=self.font_mini, align="center")
            self.draw.multiline_text((score_position, 15), score, fill=(255, 255, 255), font=self.font, align="center")
            self.draw.multiline_text((time_period_pos, 5), time_period, fill=(255, 255, 255), font=self.font_mini, align="center")

            # # Only show the period if the game ended in Overtime "OT" or Shootouts "SO"
            # if period == "OT" or period == "SO":
            #     period_position = center_text(self.font_mini.getsize(period)[0], 32)
            #     self.draw.multiline_text((period_position, 11), period, fill=(255, 255, 255), font=self.font_mini,align="center")

            # # Open the logo image file
            # away_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['away_team_id']]['abbreviation']))
            # home_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['home_team_id']]['abbreviation']))

            # # Set the position of each logo on screen.
            # away_team_logo_pos = self.screen_config.team_logos_pos[str(overview['away_team_id'])]['away']
            # home_team_logo_pos = self.screen_config.team_logos_pos[str(overview['home_team_id'])]['home']

            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)

            # Put the images on the canvas
            #self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
            #self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])

            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

        else:
            # (Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            time.sleep(60)  # sleep for 1 min

    def _draw_goal(self):

        debug.info('SCOOOOOOOORE, MAY DAY, MAY DAY, MAY DAY, MAY DAAAAAAAAY - Rick Jeanneret')
        # Load the gif file
        im = Image.open("Assets/goal_light_animation.gif")
        # Set the frame index to 0
        frameNo = 0

        self.canvas.Clear()

        # Go through the frames
        x = 0
        while x is not 5:
            try:
                im.seek(frameNo)
            except EOFError:
                x += 1
                frameNo = 0
                im.seek(frameNo)

            self.canvas.SetImage(im.convert('RGB'), -16, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            frameNo += 1
            time.sleep(0.1)

    def _draw_off_day(self):
        self.draw.text((7,3), "off", fill='orange', font=self.font_score)
        self.draw.text((7,16), "DAY", fill='orange', font=self.font_score)
        #self.draw.text((0, -1), 'NO\n GAME\n TODAY', font=self.font_abbvr)
        self.canvas.SetImage(self.image, 0,0)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        time.sleep(5)
        fav_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[self.data.fav_team_id]['abbreviation']))
        self.canvas.SetImage(fav_team_logo.convert("RGB"), 0, 0)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)