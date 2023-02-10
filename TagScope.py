#!/usr/bin/env python
import PySimpleGUI as sg
import random


import PySimpleGUI as sg
import random



class Bar_Graph:
    def __init__(self, key : str, graph_size: tuple[int, int]):
        self.key = key
        self.graph_size_x, self.graph_size_y = graph_size
        layout = [[sg.Graph(graph_size,(0, -self.graph_size_y/2), (self.graph_size_x, self.graph_size_y/2), k=self.key)]]
        self.layout = sg.Frame(title = self.key, layout = layout)
        

    def start_plotting(self, window):
        self.graph = window[self.key]     # type:sg.Graph

    def update(self,  labels: list[str], consumption, generation):
        bar_spacing = self.graph_size_x/len(consumption) #finds the x limit for each bar
        bar_width = .6 * bar_spacing
        edge = .1 * bar_spacing
        self.graph.erase()
        for i in range(len(consumption)) :
            self.graph.draw_rectangle(top_left=(i * bar_spacing + edge, consumption[i]),
                                bottom_right=(i * bar_spacing + edge + bar_width, 0),
                                fill_color='green', line_width=0)

            self.graph.draw_rectangle(top_left=(i * bar_spacing + edge, 0),
                                bottom_right=(i * bar_spacing + edge + bar_width, -generation[i]),
                                fill_color='red', line_width=0)  

            self.graph.DrawText(labels[i],(i * bar_spacing + edge + bar_width / 2 ,self.graph_size_y/3),angle = 60,color = 'white',)

sg.theme('black')

STEP_SIZE = 1
SAMPLES = 300
SAMPLE_MAX = 300
CANVAS_SIZE = (300, 300)

class pen:
    def __init__(self,graph, ref, color = None, ) -> None:
        self.graph = graph
        self.prev_x, self.prev_y = 0, 0
        self.graph_value = 250
        self.figures = []
        self.color = 'white' if not color else color
        self.update_ref = ref

    def update(self, i, length):
        self.graph_value = self.update_ref()
                    #used to cap off values
        if self.graph_value > SAMPLE_MAX:
            self.graph_value = SAMPLE_MAX
        if self.graph_value < 0:
            self.graph_value = 0

        new_x, new_y = i, self.graph_value
        #move all segments down 
        if i >= length:
            self.graph.delete_figure(self.figures[0])
            self.figures = self.figures[1:]
            for count, figure in enumerate(self.figures):
                self.graph.move_figure(figure, -STEP_SIZE, 0)
            self.prev_x = self.prev_x - STEP_SIZE

        #draw the next line segment
        last_figure = self.graph.draw_line((self.prev_x, self.prev_y), (new_x, new_y), color= self.color)
        self.figures.append(last_figure)
        self.prev_x, self.prev_y = new_x, new_y

class line_graph:
    def __init__(self, key, data, canvass_size, domain_range) -> None:
        self.i = 0
        self.key = key
        self.data = data
        self.canvass_x, self.canvass_y = canvass_size
        self.domain, self.range = domain_range
        self.layout = sg.Frame(title = self.key, layout = [
                        [sg.Graph((self.canvass_x,self.canvass_y),  (0, 0), (self.domain, self.range),
                                    background_color='black', key= self.key)
                        ]])
     
    def start_plotting(self, window):
        graph = window[self.key]     # type:sg.Graph        

        #y axixs
        graph.draw_line((20, 0), (20,self.range),color='white')
        for tic in [i*self.range/5 for i in range(5)]:
            graph.DrawText(f"{tic:.0f}",(10,tic + 5),color = 'white',) 

        #x axicks
        graph.draw_line((20,self.range/2), (self.domain, self.range/2),color='white')
        
        #create Pens
        colors = ['red','blue','green','tan','purple','orange','violet',]
        self.pens = {k: pen(graph, v, color = color) for (k, v),color in zip(self.data.items(),colors)}
        
        #make legend
        starting_pos = (60,10)
        for name, color in self.pens.items():    
            graph.DrawText(f"{name}",starting_pos,color = color.color,text_location="center")
            starting_pos  = (starting_pos[0] ,starting_pos[1] + 15)

    def update(self):
        for pen in self.pens.values():
            pen.update(self.i , self.domain)
        self.i += STEP_SIZE if self.i < self.domain else 0

if __name__ == '__main__':
    sg.theme('Black')
    sg.set_options(element_padding=(0, 0))

    class rando():
        def __init__(self) -> None:
            self.current_value = 250
        
        def get_current(self):
            self.current_value += random.randint(-10, 10)
            if self.current_value > SAMPLE_MAX:
                self.current_value = SAMPLE_MAX
            if self.current_value < 0:
                self.current_value = 0
            return self.current_value

    a = rando()
    b = rando()
    randoms = {"Battery Current":a.get_current, "Motor Voltage": b.get_current, "Motor Power" :lambda:(a.current_value*b.current_value)//500}
    graph1 = line_graph("Power",  randoms, (400, 200) , (400, 900))
    graph2 = line_graph("Temps", randoms, (500, 100), (500,100))
    graph3 = Bar_Graph("Energy" , (400,100))
    layout = [[sg.Button('Quit', button_color=('white', 'black'))],
                [[graph1.layout],[graph3.layout]],
                [[graph2.layout]], ]

    window = sg.Window('Canvas test', layout, grab_anywhere=True,
                       background_color='black', no_titlebar=False,
                       use_default_focus=False, finalize=True)
    
    graph1.start_plotting(window)
    graph2.start_plotting(window)
    graph3.start_plotting(window)

    consumption = [0,2,500,0]
    generation = [0,30,400,0]

    def accumulated_device_energy(power):
        #power is device current*device voltage list    
        loop_time = 50
        for i in range(len(power)):
            source = power[i]
            if source < 0:
                generation[i] += source * loop_time
            else:   
                consumption[i] += source *loop_time

        return consumption, generation

    while True:
        event, values = window.read(timeout=0)
        if event == 'Quit' or event == sg.WIN_CLOSED:
            break
        
        graph1.update()
        graph2.update()
        graph3.update(*accumulated_device_energy([(a.current_value*b.current_value)]))

    window.close()






