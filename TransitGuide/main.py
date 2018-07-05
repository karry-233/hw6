#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import webapp2
from google.appengine.api import urlfetch
import json, jinja2, cgi
import networkx as nx


networkJson = urlfetch.fetch("https://tokyo.fantasy-transit.appspot.com/net?format=json").content  
# ウェブサイトから電車の線路情報をJSON形式でダウンロードする
network = json.loads(networkJson.decode('utf-8'))  
# JSONとしてパースする（stringからdictのlistに変換する）


class TransferGuide(webapp2.RequestHandler):
    
    def get(self):

        Start = jinja2.Template(  # Jinjaのテンプレートエンジンを使ってHTMLを作成
        '''
        <select name="Start">
          {% for line in network %}
            <option value="line" disabled>--------------</option>
            <option value="line" disabled>{{line["Name"]}}</option>        
            {% for station in line["Stations"] %}
            <option value="{{station}}">{{station}}</option>
          {% endfor %}
        {% endfor %}
        </select>
        ''')

        Destination = jinja2.Template(  # Jinjaのテンプレートエンジンを使ってHTMLを作成
        '''
        <select name="Destination">
          {% for line in network %}
          <option value="line" disabled>--------------</option>
          <option value="line" disabled>{{line["Name"]}}</option>        
            {% for station in line["Stations"] %}
            <option value="{{station}}">{{station}}</option>
          {% endfor %}
        {% endfor %}
        </select>
        ''')
       
        self.response.headers["Content-Type"] = "text/html; charset=utf-8"
        self.response.out.write("""
                                <html>
                                  <head>
                                    <title>TransferGuide</title>
                                  </head>
                                  <body>
                                    <h1>Are you getting lost in Tokyo? <br></h1>
                                    <img src="https://images.unsplash.com/photo-1494587416117-f102a2ac0a8d?ixlib=rb-0.3.5&ixid=eyJhcHBfaWQiOjEyMDd9&s=636b63868b175036ffcd49877df723e9&auto=format&fit=crop&w=1050&q=80" width="600" height="400">
                                    <br>-----------------------------------------------------------------------------------------------------------------<br>
                                    <h2>Don't worry! Let us help you! :) <br></h2>
                                    <form action="/output" method="post">Start from:<br>
                                """)
        self.response.write(Start.render(network=network))
        self.response.out.write("""<br><br>Destination:<br>
                                """)
        self.response.write(Destination.render(network=network))   
        self.response.out.write("""    
                                    <form action="/output" method="post">
                                      <br><input type="submit" value="Search">
                                    </form>
                                  </body>
                                </html>
                                """)


            
class TransferGuide_Output(webapp2.RequestHandler):
    
    def post(self):    
    
        def build_graph():
            g = nx.Graph()
    
            #add nodes to graph
            nodes_list = []
            for line in network:
                for station in line['Stations']:
                    if station not in nodes_list:
                        nodes_list.append(station)
            g.add_nodes_from(nodes_list)
    
            #add edges to graph
            edges_list = []
            for line in network:
                for i in range(len(line['Stations'])-1):
                    edges_list.append((line['Stations'][i],line['Stations'][i+1],{'line':line['Name']}))
            g.add_edges_from(edges_list)
            
            return g


        def find_path(start, dest):
            g = build_graph()
            path = nx.shortest_path(g, start, dest)
            return g,path      

    
        def find_transit_stations(start,dest):
            g, path = find_path(start,dest)
            transit_stations = {}
            result = [start+'('+g[path[0]][path[1]]['line']+')']
            for i in range(1,len(path)-1):
                line_info1 = g[path[i-1]][path[i]]['line']
                line_info2 = g[path[i]][path[i+1]]['line']
                if line_info1 != line_info2:
                    transit_stations[path[i]] = line_info2 
            for transit_station in transit_stations:
                result.append(transit_station+'('+transit_stations.get(transit_station)+')')
            result.append(dest)
            result = '---->'.join(result)
            return result 
    
        
        self.response.headers["Content-Type"] = "text/html; charset=utf-8"
        self.response.out.write("""
                                <html>
                                  <head>
                                    <title>
                                      Transit Route
                                    </title>
                                  <head>
                                  <body>
                                    <img src="https://images.unsplash.com/photo-1494587416117-f102a2ac0a8d?ixlib=rb-0.3.5&ixid=eyJhcHBfaWQiOjEyMDd9&s=636b63868b175036ffcd49877df723e9&auto=format&fit=crop&w=1050&q=80" width="600" height="400">
                                    <br>------------------------------------------------------------------------------------------------------------------------------<br>                                  
                                    <h2>Here is your transit route^v^<br></h2>
                                """)
        result = find_transit_stations(cgi.escape(self.request.get("Start")),cgi.escape(self.request.get("Destination")))


        shortest_path = jinja2.Template(  # Jinjaのテンプレートエンジンを使ってHTMLを作成
         '''
          {% for output in result %}
           {{output}}        
          {% endfor %}
         ''')
     

        self.response.out.write(shortest_path.render(result=result))
        self.response.out.write("""
                                  </body>
                                </html>
                                """
                                )


        
app = webapp2.WSGIApplication([("/", TransferGuide),
                               ("/output", TransferGuide_Output)],
                              debug=True)

