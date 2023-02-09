import giftray

if __name__ == '__main__':
    #import itertools, glob
    a=giftray.giftray()

    '''
    import threading
    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
           pass
        else:
            ctypes.windll.user32.PostThreadMessageW(t.native_id, win32con.WM_QUIT, 0, 0)
    '''
