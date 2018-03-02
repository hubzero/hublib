Util Module
===========

This module contains functions that support launching 
web tools in HUBzero containers.

.. function:: get_proxy_addr()

  For web tools running in a HUBzero container, returns the path
  and URL.

 :return: A tuple containing the path and the full url for the HUBzero container.  If this code is not in a HUB container, it will return a path of "/" and an empty string ("") for the url.

  >>> get_proxy_addr()
  ('/weber/19158/ueeOziQBKV1GCU6N/81/',
  'https://proxy.help.hubzero.org/weber/19158/ueeOziQBKV1GCU6N/81/')


.. function:: get_cookie()

  Returns the cookie name and value for a HUBzero container.  Web tools
  that do their own security checking will need to check the received cookies
  for a matching name and value.  Cookies are set when launching a tool
  from HUBzero, so browsers without the cookie will not be able to connect to the running web tool.

 :return: A tuple containing (name, value).  Empty strings are returned if the code is run outside a HUBzero container.

  >>> get_cookie()
  ('weber-auth-help-hubzero-org', '19159:e6baae54ba5ed9c6')


.. function:: check_access(app)

  For `Dash`_ applications, provide cookie-based authentication. For the server, port must be 8000 and host '0.0.0.0'.

  :param app: a Dash object.
   
  ::

      import dash
      import dash_core_components as dcc
      import dash_html_components as html

      from hublib.util import get_proxy_addr, check_access

      app = dash.Dash(url_base_pathname=get_proxy_addr()[0])
      check_access(app)

      app.layout = html.Div(children=[
          html.H1(children='Hello Dash'),

          html.Div(children='''
              Dash: A web application framework for Python.
          '''),

          dcc.Graph(
              id='example-graph',
              figure={
                  'data': [
                      {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                      {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                  ],
                  'layout': {
                      'title': 'Dash Data Visualization'
                  }
              }
          )
      ])

      if __name__ == '__main__':
          app.run_server(port=8000, host='0.0.0.0')


.. _Dash: https://plot.ly/products/dash/