""" Serves planning.domains sessions data """

from flask import Flask, jsonify, Response, request
app = Flask(__name__)

@app.route('/')
def test_page():
    """ Renders a test page """
    return '<h1>Editor.Planning.Domains mock</h1><br/>Click <a href="vscode://jan-dolejsi.pddl/planning.domains/load_session/123456789aBcD">here</a> to open the session in VS Code.'

# mock sessions
SESSIONS = {}
# mock session content
DEFAULT_SESSION_FILE_NAMES = ["domain.pddl", "problem1.pddl", "problem2.pddl"]

@app.route('/session/<session_id>')
def get_session(session_id):
    """ Returns the session content """

    if session_id not in SESSIONS:
        SESSIONS[session_id] = {file_name: create_mock_file_content(session_id, file_name)
                                for file_name in DEFAULT_SESSION_FILE_NAMES}

    session_info = {
        "sessionId": session_id,
        "readOnly": False,
        "files": [file_name for file_name in SESSIONS[session_id].keys()]
    }

    return jsonify(result=session_info)

@app.route('/session/<session_id>/<file_name>')
def get_file(session_id, file_name):
    """ Returns the file content """

    if session_id not in SESSIONS:
        return Response(status=404)

    if file_name not in SESSIONS[session_id]:
        return Response(status=404)

    file_content = SESSIONS[session_id][file_name]

    resp = Response(response=file_content, status=200, mimetype="text/plain")
    resp.headers["Content-Type"] = "text/plain; charset=utf-8"
    return resp

@app.route('/session/<session_id>/<file_name>', methods=['POST'])
def post_file(session_id, file_name):
    """ Creates a new session file with given content """

    if session_id not in SESSIONS:
        return Response(status=404)

    session = SESSIONS[session_id]

    if file_name in session:
        return Response(status=409)

    content = request.get_data()
    session[file_name] = content

    app.logger.debug('New file added to the session {}'.format(file_name))

    resp = Response(response=content, status=201, mimetype="text/plain")
    resp.headers["Content-Type"] = "text/plain; charset=utf-8"
    return resp

@app.route('/session/<session_id>/<file_name>', methods=['PUT'])
def put_file(session_id, file_name):
    """ Updates session file content """

    if session_id not in SESSIONS:
        return Response(status=404)

    session = SESSIONS[session_id]

    if file_name not in session:
        return Response(status=404)

    app.logger.debug('File content changed: {}'.format(file_name))

    content = request.get_data()
    session[file_name] = content

    resp = Response(response=content, status=201, mimetype="text/plain")
    resp.headers["Content-Type"] = "text/plain; charset=utf-8"
    return resp

@app.route('/session/<session_id>/<file_name>', methods=['DELETE'])
def delete_file(session_id, file_name):
    """ Removes the file from the session """

    if session_id not in SESSIONS:
        return Response(status=404)

    session = SESSIONS[session_id]

    if file_name not in session:
        return Response(status=404)

    session.remove(file_name)
    app.logger.debug('File removed from the session {}'.format(file_name))

    return Response(status=201)


def create_mock_file_content(session_id, file_name):
    """ creates mock file content """
    return """; file {} from session {}
(domain (...)
)
""".format(session_id, file_name)
