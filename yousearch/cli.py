import curses
from yousearch import youtube_api
from yousearch import mpv_api


class Cli():
    def __init__(self):
        self.screen = curses.initscr()
        self.rows, self.cols = self.screen.getmaxyx()
        self.exit_result_screen = False
        self.exit_search_screen = False
        curses.noecho()

    def show_start_screen(self):
        self.screen.clear()
        self.screen.addstr("Welcome to YouSearch!\n\n")
        self.screen.addstr("Enter a YouTube URL: ")
        self.screen.refresh()
        curses.echo()
        url = self.screen.getstr()
        curses.noecho()
        return url.decode()

    def show_browse_screen(self):
        self.screen.clear()
        self.screen.addstr("Search for: ")
        self.screen.refresh()
        curses.echo()
        keystring = self.screen.getstr()
        curses.noecho()
        return keystring.decode()

    def get_direction(self, pad):
        while True:
            key = pad.getch()
            if key == curses.KEY_UP or key == 16:
                return -1
            if key == curses.KEY_DOWN or key == 14:
                return 1
            if key == curses.KEY_ENTER or key == 10:
                return 2
            if key == ord('q'):
                self.exit_result_screen = True
                return 3

    def show_search_results(self, results):
        self.screen.clear()
        pad = curses.newpad(len(results)+2, self.cols)
        pad_rows, pad_cols = pad.getmaxyx()
        pad.addstr("Select a result to start the video!")
        pad.keypad(True)
        line_pointer = 2
        cursor_pointer = 2
        for result in results:
            pad.addstr(line_pointer, 1,
                       f"{line_pointer - 1}. {result['text']}")
            line_pointer += 1

        enter_flag = False
        while not enter_flag and not self.exit_result_screen:
            pad.move(cursor_pointer, 0)
            pad.chgat(curses.A_REVERSE)
            if cursor_pointer >= self.rows:
                pad.refresh(cursor_pointer - self.rows + 1, 0,
                            0, 0, self.rows - 1, self.cols - 1)
            else:
                pad.refresh(0, 0, 0, 0, self.rows - 1, self.cols - 1)
            key = self.get_direction(pad)
            pad.chgat(curses.A_NORMAL)
            if key == 2:
                enter_flag = True
            elif cursor_pointer + key in range(2, pad_rows):
                cursor_pointer += key
        return cursor_pointer - 2

    def start_video_screen(self):
        self.screen.clear()
        self.screen.addstr("Starting video...")
        self.screen.refresh()

    def cli(self):
        while True:
            url = self.show_start_screen()
            video = youtube_api.Video(url)

            while not self.exit_search_screen:
                keystring = self.show_browse_screen()
                search_result = video.search_string(keystring)
                if len(search_result) == 0:
                    continue

                while not self.exit_result_screen:
                    result_index = self.show_search_results(search_result)
                    if not self.exit_result_screen:
                        self.start_video_screen()
                        mpv_api.start_video(
                            url, search_result[result_index]["start"] - 1.5)
                        self.screen.clear()
                        self.screen.refresh()

                self.exit_result_screen = False
            self.exit_search_screen = False


def main():
    cli = Cli()
    cli.cli()


if __name__ == '__main__':
    main()
