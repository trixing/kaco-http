# A fake Kaco Inverter with static responses
# Useful for reverse engineering the behavior
# of the Kaco NX Setup App
#
# Copyright 2022 by Jan Dittmer <jdi@l4x.org>
#
#
from flask import Flask, Response, jsonify
from flask import request
import json


app = Flask(__name__)


@app.route('/setting.cgi', methods=['POST'])
def setting():
    return jsonify({'dat': 'ok'})


@app.route('/getdevdata.cgi', methods=['GET'])
def getdevdata(device=2, sn="1234"):
  content = '{"flg":1,"tim":"20221111153846","tmp":351,"fac":4998,"pac":0,"sac":0,"qac":0,"eto":464,"etd":61,"hto":59,"pf":0,"wan":0,"err":0,"vac":[2325,2327,2341],"iac":[5,5,5],"vpv":[1500,1497],"ipv":[0,1],"str":[]}'
  return Response(content, mimetype='application/json')


@app.route('/getdev.cgi', methods=['GET'])
def getdev(device=0):
    if request.args.get('device', 0) == "2":
        content = '{"inv":[{"isn":"8.0NX312001234","add":3,"safety":70,"rate":8000,"msw":"V610-03043-04 ","ssw":"V610-60009-00 ","tsw":"V610-11009-01 ","pac":386,"etd":58,"eto":461,"err":0,"cmv":"V2.1.1AV2.00","mty":51,"psb_eb":1}],"num":1}'
    else:
        content = '{"psn":"1234567890","key":"1234567890","typ":5,"nam":"Wi-Fi Stick","mod":"B32078-10","muf":"KACO","brd":"KACO","hw":"M11","sw":"21618-006R","wsw":"ESP32-WROOM-32U","tim":"2022-11-11 13:19:34","pdk":"","ser":"","protocol":"V1.0","host":"cn-shanghai","port":1883,"status":-1}'
    return Response(content, mimetype='application/json')

@app.route('/wlanget.cgi')
def wlanget():
   return Response('{"mode":"STATION","sid":"lasseredn","srh":-42,"ip":"10.0.0.2","gtw":"10.0.0.1","msk":"255.255.255.0"}', mimetype='application/json')


@app.route('/<path:path>', methods=['POST', 'GET'])
def catch_all(path):
    app.logger.info('Catch-All %s: %s', (path, request.data))
    return 'Not implemented path: %s' % path

@app.route('/readme')
def readme():
   import markdown
   content = markdown.markdown(open('README.md').read())
   return '<html><body>' + content + '</body></html>'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8484)
