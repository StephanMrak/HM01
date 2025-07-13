import multiprocessing
import time
import hmsysteme
from check_for_updates import CheckForUpdates, UpdateSystem



width = '100%'
height = '1000px'
abt=[]

def start_game(gamefile, backgroundqueue):
    #backgroundqueue.put("close")
    hmsysteme.open_game()
    time.sleep(0.5)
    mod_game=(__import__(gamefile))
    print(mod_game)
    p = multiprocessing.Process(target=mod_game.main)
    print(p)
    p.start()
    #time.sleep(1)
    return p

    
def close_game(asd, abt, backgroundqueue):
    for i in range(0,len(asd)):
        if asd[i].is_alive():           
            hmsysteme.close_game()
            hmsysteme.put_button_names(False)
            time.sleep(0.5)
            asd[i].terminate()
            print(asd[i])
    try:
        for i in range(0, len(abt)):
            abt[i].set_text("no function")
            abt[i].set_enabled(False)
        #backgroundqueue.put("open")
    except:
        pass


def listchecker(ele,list):
    for element in list:
        if element[0]==ele:
            return False
    return True

def mobile_com(threadname,path2,gamefiles,backgroundqueue, debug_flag):
    import time
    import io
    import os
    import PIL.Image
    asdf=[]
    backgroundqueue.put("open")

    import remi.gui as gui
    from remi import start, App
    
    path=hmsysteme.get_path()





    container_players_added = gui.VBox(width=width, height=height,
                                       style={'padding-left': '-200px', 'font-size': '15px', 'align': 'left'})
    container_players_added.style["background"] = "#404040"
    container_players_added.style["color"] = "white"
    container = gui.VBox(width=width, height=height,
                         style={'padding-left': '0px', 'font-size': '15px', 'align': 'left'})
    container.style["background"] = "#404040"
    container2 = gui.VBox(width=width, height=height,
                          style={'padding-left': '0px', 'font-size': '15px', 'align': 'left'})
    container2.style["background"] = "#404040"
    container3 = gui.VBox(width=width, height=height,
                          style={'padding-left': '0px', 'font-size': '15px', 'align': 'left'})
    container3.style["background"] = "#404040"
    container4 = gui.VBox(width=width, height=height,
                          style={'padding-left': '0px', 'font-size': '15px', 'align': 'left'})
    container4.style["background"] = "#404040"

    def fill_grid_with_playernames():
        def on_text_area_change(self, widget):

            playernames = hmsysteme.get_playerstatus()
            if playernames == False:
                playernames = []
            if txt.get_text() != "" and len(txt.get_text())<20:
                if listchecker(txt.get_text(),playernames)==True:

                    playernames.append([txt.get_text(),True])
                    txt.set_text("")
                    hmsysteme.put_playernames(playernames)
                    fill_grid_with_playernames()

        if hmsysteme.get_playerstatus() != False:
            playernames = hmsysteme.get_playerstatus()
        else:
            playernames=[]
        lbl = gui.Label('input player name: ', width='50%', height='35px',
                              style={'font-size': '25px', 'text-align': 'left'})
        lbl.style["color"] = "white"

        txt = gui.TextInput(width='30%', height='35px', style={'font-size': '30px', 'text-align': 'left'})
        txt.style["background"] = "#606060"
        txt.style["color"] = "white"
        txt.onchange.do(on_text_area_change)
        container2.empty()
        container2.append(lbl)
        container2.append(txt)
        txtblank=gui.Label('', width='50%', height='35px',
                              style={'font-size': '25px', 'text-align': 'left'})
        container2.append(txtblank)

        grid = gui.GridBox(width=500)
        grid.style["background"] = "#404040"
        grid.style["color"] = "white"
        asd = []
        checka = []
        deletea=[]
        functionsc = []
        deletefunctions=[]
        for i in range(0, len(playernames)):
            asd.append(['delete' + str(i + 1),'check' + str(i + 1), 'label' + str(i + 1)])
        grid.define_grid(asd)
        for i in range(0, len(playernames)):
            checka.append(gui.CheckBox(playernames[i][1],width='50px', height='50px' ,margin='1%',style={'font-size': '20px', 'text-align': 'center'}))
            button=gui.Button('DELETE',width='130px', height='50px' ,margin='1%',style={'font-size': '20px', 'text-align': 'center'})
            button.style["background"] = "red"
            button.style["box-shadow"] = "none"
            deletea.append(button)

            def f(widget, newValue, i=i):
                if newValue == True:
                    playernames[i][1] = True
                else:
                    playernames[i][1] = False
                hmsysteme.put_playernames(playernames)


            def deletefunction(widget,i=i):
                playernames.pop(i)
                hmsysteme.put_playernames(playernames)
                fill_grid_with_playernames()




            functionsc.append(f)
            deletefunctions.append(deletefunction)
            checka[i].onchange.do(functionsc[i])
            deletea[i].onclick.do(deletefunctions[i])


            lbl = gui.Label(playernames[i][0], width='300px', height='50px' ,margin='1%',style={'font-size': '30px', 'text-align': 'left'})
            grid.append({'delete' + str(i + 1): deletea[i],'label' + str(i + 1): lbl, 'check' + str(i + 1): checka[i]})
            grid.set_row_gap(20)
            grid.set_column_gap(20)
        container2.append(grid)





    class PILImageViewverWidget(gui.Image):
        def __init__(self, pil_image=None, **kwargs):
            super(PILImageViewverWidget, self).__init__(os.path.join(path,"screencapture.jpg"), **kwargs)
            #super(PILImageViewverWidget, self).__init__(r"C:\Users\49176\Dropbox\HM01", **kwargs)
            #super(PILImageViewverWidget, self).__init__("/home/stan/Dropbox/HM01/screen_capture.png", **kwargs)
            
            self._buf = None

        def load(self, file_path_name):
            pil_image = PIL.Image.open(file_path_name)
            self._buf = io.BytesIO()
            pil_image.save(self._buf, format='JPEG')
            self.refresh()

        def refresh(self):
            i = int(time.time() * 1e6)
            self.attributes['src'] = "/%s/get_image_data?update_index=%d" % (id(self), i)

        def get_image_data(self, update_index):
            if self._buf is None:
                return None
            self._buf.seek(0)
            headers = {'Content-type': 'image/jpg'}
            return [self._buf.read(), headers]
    
        
    
    class HMInterface(App):
        def __init__(self, *args):
            super(HMInterface, self).__init__(*args)
            
        def idle(self):
            time.sleep(0.1)
            if hmsysteme.screenshot_refresh()== True:
                self.image_widget.load(file_path_name=os.path.join(path,"screencapture.jpg"))



            if hmsysteme.game_isactive():
                a = hmsysteme.get_button_names()
                if a!= False:
                    try:
                        for i in range(0, len(abt)):
                            if i < len(a):
                                abt[i].set_text(a[i])
                                abt[i].set_enabled(True)
                            else:
                                abt[i].set_text("no function")
                                abt[i].set_enabled(False)
                    except:
                        pass



            
           
        def main(self):
            bt=[]
            global abt
            functions=[]
            global width
            global height
            tb = gui.TabBox(width=width ,style={'color': 'white', 'background-color': '#404040','font-size':'20px'})


            #container = gui.VBox(width=500, height=650)



            
            self.lbl = gui.Label('no game running yet', width='100%', height='35px',style={'font-size': '25px', 'text-align': 'left'})#str(q.get()))
            self.lbl.style["color"]="white"
            self.lbl_foto = gui.Label('-')
            self.lbl_count = gui.Label('-')
            
            for i in range (len(gamefiles)):
                bt.append(gui.Button('run %s' %(str(gamefiles[i])),width='31%', height='50px' ,margin='1%',style={'font-size': '20px', 'text-align': 'center'}))
                bt[i].style["background"] = "#606060"
                bt[i].style["box-shadow"] = "none"
                
            b1 = gui.Button('Close all',width='31%', height='50px' ,margin='1%',style={'font-size': '20px', 'text-align': 'center'})
            b1.style["background"] = "#606060"
            b1.style["box-shadow"] = "none"
            b2 = gui.Button('Stop Server',width='31%', height='50px' ,margin='1%',style={'font-size': '20px', 'text-align': 'center'})
            b2.style["background"] = "#606060"
            b2.style["box-shadow"] = "none"
            b3 = gui.Button('System Shutdown',width='31%', height='50px' ,margin='1%',style={'font-size': '20px', 'text-align': 'center'})
            b3.style["background"] = "#606060"
            b3.style["box-shadow"] = "none"
            b4 = gui.Button('System reset',width='31%', height='50px' ,margin='1%',style={'font-size': '20px', 'text-align': 'center'})
            b4.style["background"] = "#606060"
            b4.style["box-shadow"] = "none"
            b5 = gui.Button('System reboot',width='31%', height='50px' ,margin='1%',style={'font-size': '20px', 'text-align': 'center'})
            b5.style["background"] = "#606060"
            b5.style["box-shadow"] = "none"
            b6 = gui.Button('Check for Updates',width='31%', height='50px' ,margin='1%',style={'font-size': '20px', 'text-align': 'center'})
            b6.style["background"] = "#606060"
            b6.style["box-shadow"] = "none"


            #self.image_widget = PILImageViewverWidget(width=width, height=height)
            self.image_widget = PILImageViewverWidget(width=width)
            self.image_widget.load(file_path_name=os.path.join(path2,"logo.jpg"))

            for i in range(0,9):
                def f(widget, i=i):
                    hmsysteme.put_action(i+1)
                    print("action button "+str(i+1)+" pressed")
                name="no function"
                action_button=gui.Button(name, width='31%', height='50px', margin='1%', style={'font-size': '20px', 'text-align': 'center'})
                action_button.style["background"] = "#606060"
                action_button.style["box-shadow"] = "none"
                abt.append(action_button)
                #container.append(action_button)
                action_button.onclick.do(f)
                action_button.set_enabled(False)
            
            for i in range(len(gamefiles)):
                def f(widget,i=i):
                    close_game(asdf, abt, backgroundqueue)
                    asdf.append(start_game(gamefiles[i],backgroundqueue))
                    self.lbl.set_text(gamefiles[i]+" now runnning")
                    #print(asdf)
                functions.append(f)       
            
            # setting the listener for the onclick event of the button
            for i in range (len(gamefiles)):
                bt[i].onclick.do(functions[i])


            b1.onclick.do(self.on_button_pressed1)
            b2.onclick.do(self.on_button_pressed2)
            b3.onclick.do(self.on_button_pressed3)
            b4.onclick.do(self.on_button_pressed4)
            b5.onclick.do(self.on_button_pressed5)
            b6.onclick.do(self.on_button_pressed6)


            

            # appending a widget to another, the first argument is a string key
            container.append(self.lbl)

            
            for i in range (len(gamefiles)):
                container3.append(bt[i])
            container.append(self.image_widget)
            #container.append(self.lbl_foto)
            #container.append(self.lbl_count)

            for i in range(0, len(abt)):
                container.append(abt[i])


            container4.append(b1)
            container4.append(b2)
            container4.append(b3)
            container4.append(b4)
            container4.append(b5)
            container4.append(b6)




            #fill container2 with player commands and active players
            fill_grid_with_playernames()


            #create label for temp
            self.templbl= gui.Label('temp ', width='50%', height='35px',style={'font-size': '25px', 'text-align': 'left'})
            self.templbl.style["color"]="white"
            container4.append(self.templbl)

            self.debuglbl= gui.Label('debugging ', width='50%', height='35px',style={'font-size': '25px', 'text-align': 'left'})
            self.debuglbl.style["color"]="white"
            container4.append(self.debuglbl)
            #container2.append(container_players_added)

            tb.append(container,'Home')
            tb.append(container2,'Players')
            tb.append(container3, 'Games')
            tb.append(container4, 'Settings')
            
            
            # returning the root widget
            return tb
            
        def on_button_pressed1(self, widget):
            global abt
            close_game(asdf, abt, backgroundqueue)

            self.lbl.set_text("no game running yet")
            print("all closed")    
            
        def on_button_pressed2(self, widget):           
            self.server.server_starter_instance._alive=False
            self.server.server_starter_instance._sserver.shutdown()
            print("server stopped")
            
        def on_button_pressed3(self, widget):
            self.dialog = gui.GenericDialog(width=350,title='Shutdown', message='Do you really want to shutdown the system')
            self.dialog.confirm_dialog.do(self.sd_func)
            self.dialog.show(self)
            
        def on_button_pressed4(self, widget):           
            self.reset_func(self)

        def on_button_pressed5(self, widget):
            self.dialog = gui.GenericDialog(width=350,title='Reboot', message='Do you really want to reboot the system')
            self.dialog.confirm_dialog.do(self.rb_func)
            self.dialog.show(self)

        def on_button_pressed6(self, widget):
            if CheckForUpdates():
                self.dialog = gui.GenericDialog(width=350, title='Update available',
                                                message='Do you really want to update? The System will be restarted!')
                self.dialog.confirm_dialog.do(self.up_func)
                self.dialog.show(self)
            else:
                self.dialog = gui.GenericDialog(width=350, title='No Update available',
                                                message='No update available')
                self.dialog.show(self)






        # def on_button_clear_names(self, widget):
        #     print("Player names cleared")
        #     hmsysteme.clear_playernames()

        def sd_func(self, widget):		
            import os
            print("system shutdown")
            os.system("sudo poweroff")

        def rb_func(self, widget):
            import os
            print("system reboot")
            os.system("sudo reboot")


        def up_func(self,widget):
            UpdateSystem()








    # starts the web server
    if debug_flag:
        start(HMInterface,start_browser=False)
    else:
        start(HMInterface, address='0.0.0.0', port=8081, multiple_instance=False, enable_file_cache=True, update_interval=0.1, start_browser=False)
    
