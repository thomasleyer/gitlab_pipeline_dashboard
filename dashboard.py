import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
import pandas as pd
from dash.dependencies import Input, Output
import gitlab

gl = gitlab.Gitlab('http://localhost', private_token='XXXXXXXXXXXXXXXXXXX')
gl.auth()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    html.Div([
        html.H4('Pipelinestatus'),
        html.Div(id='pipelines'),
#        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1 * 5000,  # in milliseconds
            n_intervals=0
        )
    ])
)

def Table(dataframe):
    rows = []
    for i in range(len(dataframe)):
        row = []
        for col in dataframe.columns:
            value = dataframe.iloc[i][col]
            # update this depending on which
            # columns you want to show links for
            # and what you want those links to be
            if col == 'web_url':
                cell = html.Td(html.A(href=value, children=value))
            else:
                cell = html.Td(children=value)
            row.append(cell)
        rows.append(html.Tr(row))
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        rows
    )


@app.callback(Output('pipelines', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    data = []
    try:
        projects = gl.projects.list(all=True)
    except:
        print ("There was a problem in retrieving projects")

    for project in projects:
        try:
            proj = gl.projects.get(project.id)
        except:
            print ("There was a problem retrieving project details for " + str(project))
        else:
            try:
                pipelines = project.pipelines.list()
            except:
                print ("There was a problem retrieving the pipeline")
            else:
                nonsuccess = 0
                for pipeline in pipelines:
                    if (pipeline.status == "success"):
                        nonsuccess = 1
                    else:
                        data.append([proj.name, pipeline.status, proj.web_url])
    print(data)
    df = pd.DataFrame(data, columns=['Name', 'status', 'web_url'])
#    is_running = df['status'] == "cancelled"
#    df_running = df[is_running]
    return Table(df)


if __name__ == '__main__':
    app.run_server(debug=True)
