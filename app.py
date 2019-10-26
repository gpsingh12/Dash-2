import pandas as pd
import requests
import json

r = requests.get('https://data.cityofnewyork.us/resource/uvpi-gqnh.json')
x = r.json()
df = pd.read_json(json.dumps(x))
df=pd.DataFrame(df)

df2 =  df[['tree_id' ,'health','spc_common', 'boroname', 'steward']] # select columns

print(df2.isnull().sum())
df2=df2.dropna()
print(df2.isnull().sum())



q2= df2.groupby(['boroname','spc_common', 'health', 'steward'])['tree_id'].nunique().reset_index()

q2['proportion'] = q2.groupby(['boroname', 'spc_common', 'steward']).transform(lambda x: 100*(x/x.sum()))
q2.head(n=10)


import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div([
    html.H2('NYC TREE HEALTH'),
    html.Label("Choose a Species"),
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': i, 'value': i} for i in q2.spc_common.unique()],
        value='American elm',
        style={'width':'50%'}
    ),
       html.Label('Select Steward'),
       dcc.RadioItems(
        id='radio',
        options=[{'label': i, 'value': i} for i in q2.steward.unique()],
 
    value=''
),
  
    
    html.Div(id='display-value'),
    dcc.Graph( id="output-graph"),
    
    

    
    
])

q2_1 = q2.loc[q2['health']=='Fair']
q2_2 = q2.loc[q2['health']=='Good']
q2_3 = q2.loc[q2['health']=='Poor']

@app.callback(dash.dependencies.Output('output-graph', 'figure'),
              [dash.dependencies.Input('dropdown', 'value'),
              dash.dependencies.Input('radio', 'value')
              ])
             #
def update_value(input1, input2):
  #  test =test[test['spc_common']=='value']
    return({'data': [
        {'x': q2.boroname.unique(), 'y': q2_1.loc[(q2_1['spc_common']==input1) 
                                                   & (q2_1['steward']==input2)].proportion, 'type': 'bar', 'name': u'Fair'},
        {'x': q2_2.boroname.unique(), 'y': q2_2.loc[(q2_2['spc_common']==input1) & (q2_2['steward']==input2)].proportion, 'type': 'bar', 'name': u'Good'},
        {'x': q2_3.boroname.unique(), 'y': q2_3.loc[(q2_3['spc_common']==input1) & (q2_3['steward']==input2)].proportion, 'type': 'bar', 'name': u'Poor'},
    ],
            'layout': {
                'title': 'Tree Health by Borough',
                'plot_bgcolor':colors['background'],
                'paper_bgcolor':colors['background'],
                'font': {
                    'color':colors['text']
                }
                
            }
        }
    )




def display_value(value):
    return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
    app.run_server()
