#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import inspect
import json
import os
import os.path
import random
import subprocess

import falcon


SERVER_FILE = inspect.getfile(inspect.currentframe())
BASE_DIR = os.path.dirname(os.path.dirname(SERVER_FILE))

_SCRIPT_CACHE = collections.defaultdict(str)

def _setup_script_cache():
    cwd = os.getcwd()
    os.chdir(os.path.join(BASE_DIR, "scrape"))

    unmerged = collections.defaultdict(list)
    with open('./script.jl') as stream:
        for line in stream:
            data = json.loads(line)
            actor = data['actor'].lower()
            line = data['line'].lower()
            unmerged[actor].append(line)

    for actor, line in unmerged.items():
        _SCRIPT_CACHE[actor] = ''.join(line)

    os.chdir(cwd)


_setup_script_cache()


class ImageEndpoint(object):

    def on_get(self, req, resp, image_file):
        with open(os.path.join('img/', image_file), 'rb') as stream:
            resp.status = falcon.HTTP_200
            resp.body = stream.read()


class StaticHTMLEndpoint(object):

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html; charset=utf-8'

        resp.body = """
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css" integrity="sha384-9gVQ4dYFwwWSjIDZnLEWnxCjeSWFphJiwGPXr1jddIhOegiu1FwO5qRGvFXOdJZ4" crossorigin="anonymous">

    <title>Gilmore Girl Dialogue Generator</title>
</head>
<style>
* {
  box-sizing: border-box;
}

.column {
  float: left;
  width: 33.33%;
  padding: 5px;
}

/* Clearfix (clear floats) */
.row::after {
  content: "";
  clear: both;
  display: table;
}
</style>

<body>
    <div class="container mt-5">
        <form>
            <div class="form-group row form-inline">
                <label for="roleSelector" class="col-sm-1 col-form-label form-label-sm">Role</label>
                <div class="col-sm-1">
                    <select id="roleSelector" class="form-control form-control-sm">
                        <option value="rory">Rory</option>
                        <option value="lorelai">Lorelai</option>
                    </select>
                </div>
                <label for="seedInput" class="col-sm-2 col-form-label col-form-label-sm">Leading Seq Input:</label>
                <div class="col-sm-2">
                    <input id="seedInput" class="form-control form-control-sm w-70" value=""/>

                </div>
                <div class="col-sm-2">
                    <button id="generateSeedButton" type="button" class="btn btn-secondary btn-sm">Generate Seq</button>
                </div>
                <label for="outputLengthInput" class="col-sm-2 col-form-label col-form-label-sm w-80">Output Length:</label>
                <div class="col-sm-1">
                    <input id="outputLengthInput" class="form-control form-control-sm w-100" value="300"/>
                </div>
                <div>
                    <button id="submit" type="button" class="btn btn-primary btn-sm" disabled>Submit</button>
                </div>
            </div>
        </form>
        <div class="row">
            <div class="column">
                <img src="img/img1.jpg" alt="" style="width:100%">
            </div>
            <div class="column">
                <img src="img/img2.jpg" alt="" style="width:100%">
            </div>
            <div class="column">
                <img src="img/img6.jpg" alt="" style="width:100%">
            </div>
        </div>
        <h4>Follow these steps:</h4>
        <div id="introDiv">
            <li>Select your favorite Gilmore Girl from the <b>Role</b> dropdown list</li>
            <li>Input any 40-character long <b>leading sequence/partical sentence</b> </li>
            <li>Or simply hit the <b>Generate Seq</b> button to generate random sequence </li>
            <li>Input a number between 100 and 400 for the <b>output length</b> (default 200 character) </li>
            <li> Hit <b>Submit</b> and wait for your result </li>
            Note: the leading seed will be displayed before the generated text.
        </div>


        <div id="messageDiv" class="alert alert-primary" role="alert">
            Are you ready?
        </div>

        <div id="resultContainer">
            <ul class="list-group" id="resultList">
            </ul>
        </div>
    </div>

     <script type="text/javascript">
document.querySelector('form').onsubmit = function() {
    return false;
};

document.getElementById("generateSeedButton").onclick = function() {
    var xhr = new XMLHttpRequest();

    xhr.onload = function() {
        if (xhr.status == 200) {
            var response = xhr.responseText;
            var seed = document.getElementById("seedInput")

            seed.value = response;
            seed.dispatchEvent(new Event('input'));
        }
    };

    var role = document.getElementById("roleSelector").value;

    xhr.open('GET', "seed?role=" + role);
    xhr.send();
};

document.getElementById("seedInput").addEventListener(
    'input',
    function(event) {
        var problems = [];

        if (this.value.length !== 40) {
            problems.push("The seed needs to have exactly 40 characters, got " + this.value.length);
        }

        var submitButton = document.getElementById("submit");
        var messageDiv = document.getElementById("messageDiv");
        if (problems.length === 0) {
            messageDiv.classList.remove("alert-warning");
            messageDiv.classList.add("alert-primary");
            messageDiv.innerHTML = "Ready!";

            submitButton.removeAttribute("disabled");

            return;
        }

        messageDiv.innerHTML = problems.join("<br/>");
        messageDiv.classList.remove("alert-primary");
        messageDiv.classList.add("alert-warning");

        submitButton.setAttribute("disabled", null);
    }
);


document.getElementById("submit").onclick = function() {
    var submitButton = this;
    var xhr = new XMLHttpRequest();
    var messageDiv = document.getElementById("messageDiv");
    var resultList = document.getElementById("resultList");

    xhr.onload = function() {
        if (xhr.status == 200) {
            var responseJSON = JSON.parse(xhr.responseText);
            var items = [];
            messageDiv.innerHTML = "Success!";

            for (var diversity in responseJSON.result) {
                items.push("<li class=\\"list-group-item\\">" +
                            responseJSON.result[diversity] +
                            "  (Diversity: " +
                            diversity +
                            ")</li>");
            }

            resultList.innerHTML = items.join("");
        } else {

            messageDiv.innerHTML = "HTTP Error " + xhr.status;
            messageDiv.classList.remove("alert-primary");
            messageDiv.classList.add("alert-warning");
        }

        submitButton.removeAttribute("disabled");
    };

    submitButton.setAttribute("disabled", null);

    resultList.innerHTML = "";
    messageDiv.innerHTML = "Generating...";

    var role = document.getElementById("roleSelector").value;
    var seed = document.getElementById("seedInput").value;
    var outputLength = document.getElementById("outputLengthInput").value;

    xhr.open('POST', "generate");
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify({
        role: role,
        seed: seed,
        output_length: outputLength
    }));
};


    </script>

    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.0/umd/popper.min.js" integrity="sha384-cs/chFZiN24E4KMATLdqdvsezGxaGsi4hLGOzlXwp5UZB1LY//20VyM2taTB4QvJ" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js" integrity="sha384-uefMccjFJAIv6A+rW+L4AHf99KvxDjWSu1z9VI8SKNVmz4sk7buKt/6v9KI65qnm" crossorigin="anonymous"></script>
</body>
</html>
"""


class SeedGenerationEndpoint(object):

    def on_get(self, req, resp):
        role = req.get_param('role')

        try:
            line = _SCRIPT_CACHE[role]
            random_start = random.randrange(len(line) - 100)

            resp.status = falcon.HTTP_200
            resp.body = line[random_start:random_start + 40]
        except Exception as e:
            resp.status = falcon.HTTP_500
            resp.body = str(e)


class OutputGenerationEndpoint(object):

    def on_post(self, req, resp):
        request_body = json.loads(req.stream.read())

        role = request_body['role']
        seed = request_body['seed']
        output_length = request_body['output_length']

        cwd = os.getcwd()
        try:
            os.chdir(os.path.join(BASE_DIR, 'src'))
            output = subprocess.check_output([
                "python3",
                "predict.py",
                "--role",
                role,
                "--seed",
                seed,
                "--output-length",
                output_length
            ])
            resp.status = falcon.HTTP_200
            resp.content_type = "application/json"
            resp.body = output
        except Exception as e:
            resp.status = falcon.HTTP_500
            resp.body = str(e)
        finally:
            os.chdir(cwd)



app = falcon.API()
app.add_route('/', StaticHTMLEndpoint())
app.add_route('/generate', OutputGenerationEndpoint())
app.add_route('/seed', SeedGenerationEndpoint())
app.add_route('/img/{image_file}', ImageEndpoint())
