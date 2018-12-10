#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import inspect
import json
import os
import os.path
import subprocess

import falcon


SERVER_FILE = inspect.getfile(inspect.currentframe())
BASE_DIR = os.path.dirname(os.path.dirname(SERVER_FILE))


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
                <label for="seedInput" class="col-sm-1 col-form-label col-form-label-sm">Seed</label>
                <div class="col-sm-8">
                    <input id="seedInput" class="form-control form-control-sm" value=""/>
                    <button id="generateSeedButton" type="button" class="btn btn-secondary btn-sm">Generate seed</button>
                </div>
                <div>
                    <button id="submit" type="button" class="btn btn-primary btn-sm" disabled>Submit</button>
                </div>
                <label for="outputLengthInput" class="col-sm-1 col-form-label col-form-label-sm">Output Size</label>
                <div class="col-sm-3">
                    <input id="outputLengthInput" class="form-control form-control-sm" value="400"/>
                </div>
            </div>
        </form>

        <div id="messageDiv" class="alert alert-primary" role="alert">
            Hello!
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
    var result = "";
    var possibleCharacters = "abcdefghijklmnopqrstuvwxyz";

    for (var i = 0; i < 40; ++i) {
        result += possibleCharacters.charAt(Math.floor(Math.random() * possibleCharacters.length));
    }

    var seedInput = document.getElementById("seedInput");
    seedInput.value = result;

    var onInputEvent = document.createEvent("HTMLEvents");
    onInputEvent.initEvent("input", false, true);
    seedInput.dispatchEvent(onInputEvent);
};

document.getElementById("seedInput").addEventListener(
    'input',
    function(event) {
        var problems = [];

        if (this.value.length !== 40) {
            problems.push("The seed needs to have exactly 40 characters, got " + this.value.length);
        }

        for (var i = 0; i < this.value.length; ++i) {
            var char = this.value.charAt(i);
            if (!(/[a-z]/.test(char))) {
                problems.push("The seed should only contain lowercase a-z.");
                break;
            }
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
</bodY>
</html>
"""


class SeedGenerationEndpoint(object):

    def on_get(self, req, resp):
        request_body = json.loads(req.stream.read())
        role = request_body['role']
        
        cwd = os.getcwd()
        try:
            os.chdir(os.path.join(BASE_DIR, 'scrape'))
            with open('')
        except Exception as e:
            resp.status = 500
            resp.body = e
        finally:
            os.chdir(cwd)
        

class OutputGenerationEndpoint(object):

    def on_post(self, req, resp):
        request_body = json.loads(req.stream.read())

        role = request_body['role']
        seed = request_body['seed']
        output_length = request_body['output_length']

        cwd = os.getcwd()
        try:
            os.chdir(BASE_DIR)
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
            resp.status = 500
            resp.body = e
        finally:
            os.chdir(cwd)



app = falcon.API()
app.add_route('/', StaticHTMLEndpoint())
app.add_route('/generate', OutputGenerationEndpoint())
app.add_route('/seed', SeedGenerationEndpoint())
