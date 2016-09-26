// variables
window.namespace = 'NAMESPACE NOT LOADED';
var params = null;
var host = null;
var port = null;
var imgport = null;
var connected = null;
var ros = null;

var paper = Raphael(30,70,window.innerWidth,window.innerHeight);
var table_items = new Array();
var table_items_transform = new Array();
var table_objects = new Array(); 
var table;

// Scaling factor for size
var scale = 350;

// Size of table
var width = 0;
var height = 0;

//Scaled Versions
var table_xpos = 0;
var table_ypos = 0;

//Unscaled
var table_x = 0;
var table_y = 0;
var table_xext = 0;
var table_yext = 0;

var goal_x = 0;
var goal_y = 0;
var goal_radius = 0;

var offset_x = 0;
var offset_y = 0;

var canvas_offset_x = 0;
var canvas_offset_y = 0;

var box_rot = 0;
var box_xext = 0;
var box_yext = 0;
var box_start_x = 0;
var box_start_y = 0;

var fuze_ext = 0;
var glass_ext = 0;

var pop_xext = 0;
var pop_yext = 0;

var hand_x = 0;
var hand_y = 0;
var hand_xext = 0;
var hand_yext = 0;

var blocking_color = "#B40404";
var goal_color = "#04B404";
var stroke = 5;

var current_drag = -1;
var start_drag_pos = new Position(0,0);

var alert_timeout = 3000;

var keyboard_input = "none";
var sceneNum = 0;
var validMove = "True";
var inGoal = false;

/*************************************************************************************/

function getCookie(key) {
    cs = document.cookie.split(';')
    for (i=0; i < cs.length; ++i) {
        k_v = cs[i].split('=')
        if (k_v[0] === key) {
            return k_v[1];
        }
    }
    return null;
}

$(document).ready(function() {

    window.namespace = getCookie('mturk_id');
    if (window.namespace === null) {
        console.log('MTURK_ID IS NULL: WATMAN');
    }


    if (!("WebSocket" in window)) {
        $("#content").prepend('<div class="alert alert-error"><button type="button" class="close" data-dismiss="alert">&times;</button><strong>Error:</strong> Websockets not supported in this browser, cannot connect to ROS!</div>');
    }

    params = parseUri(window.location.href);
    host = window.location.hostname;
    port = params.queryKey['port'] || '9090';
    //imgport = params.queryKey['imgport'] || '9191';
    connected = true;
    //ros = new ROS('ws://' + host + ':' + port); //If Debug
    ros = new ROS('ws://' + host + ':8888');

    ros.on('close', function(e) {
        $('.ros-status').each(function() {
            $(this).removeClass('btn-success');
            $(this).removeClass('btn-warning');
            $(this).addClass('btn-danger');
            $(this).text('Disconnected');
            $('#diconnectedModal').modal('show'); 
        });
    });

    ros.on('error', function(e) {
        $('.ros-status').each(function() {
            $(this).removeClass('btn-success');
            $(this).addClass('btn-warning');
            $(this).removeClass('btn-danger');
            $(this).text('Error');
            $('#diconnectedModal').modal('show'); 
        });
    });

    ros.on('connection', function(e) {
        connected = true;
        $('.ros-status').each(function() {
            $(this).addClass('btn');
            //$(this).addClass('btn-success');
            $(this).removeClass('btn-warning');
            $(this).removeClass('btn-danger');
            $(this).text('Connected');
        });
    });

    $('.ros-status').each(function() {
        $(this).addClass('btn-danger');
        $(this).text('Disconnected');
        $(this).click(function () {
            location.reload();
        });
    });

    // Get initial list of services
    ros.getServices(function(initialServices){

        // Convert all ros-service button to service callers
        $('.ros-service').each(function() {

            // Creates a service client
            var service = new ros.Service({
                name        : $(this).attr('service'),
                serviceType : $(this).attr('type')
            });

            // Configure this button to do ROS services
            var b = $(this);
            b.addClass('btn-primary');
            b.attr('data-loading-text', 'Running...');

            // Color based on whether service exists yet
            if(jQuery.inArray(service.name, initialServices) <= 0) 
            {
                b.addClass('btn-danger');
            }

            // On click, make service call
            b.click(function() 
                    {
                        b.button('loading');

                        // Parse the provided arguments
                        args = jQuery.parseJSON(b.attr('args') || '{}');
                        console.log("Calling " + service.name + ": [" + args + "]");

                        // Make ServiceRequest containing the data to send in the service call.
                        var request = new ros.ServiceRequest(args);

                        // Start a timeout that we will cancel if the call succeeds
                        var timeoutId = setTimeout(function() {
                            console.log("Timed out response to " + service.name);
                            // Color button based on service call success
                            b.button('reset');
                            b.addClass('btn-danger')
                        }, 10000);

                        // Make the actual service call
                        service.callService(request, function(response) {
                            // Clear our timeout
                            clearTimeout(timeoutId);

                            // Log the response to the call
                            console.log("Responded " + service.name + ": ");
                            console.log(response);

                            // Color button based on service call success
                            b.button('reset');
                            b.removeClass('btn-danger');
                        });
                    });
        });
    });  // getservice

    document.onkeyup = function(e) {
        console.log("Keyboard input");

        var service = new ros.Service({
            name        : '/' + window.namespace + '/input_to_state',
            serviceType : 'user_interface/InputToState'
        });

        console.log(service);
        var request = new ros.ServiceRequest();
        console.log(request);

        if (inGoal == false) {
            switch (e.keyCode) 
            {
            case 37:
                request.input = "tleft";
                keyboard_input = "tleft";
                break;
            case 87:
                request.input = "forward";
                keyboard_input = "forward";
                break;
            case 39:
                request.input = "tright";
                keyboard_input = "tright";
                break;
            case 83:
                request.input = "backward";
                keyboard_input = "backward";
                break;
            case 65:
                request.input = "left";
                keyboard_input = "left";
                break;
            case 68:
                request.input = "right";
                keyboard_input = "right";
                break;
            };
        }

        service.callService(request, function(response)
                            {
                                validMove = response.validMove;
                                regenerateScene();
                            });     
    };


    if (connected==true)
    {
        console.log('CONNECTED: initing scene')
        initializeScene();     
    }
});
/***************************************************************************************************************/

/***************************************************************************************************************/    
function initializeScene()
{
    var d = new Date();
    var a = d.getMilliseconds()*0.000001; 
    console.log("start time " + a);
    var service = new ros.Service({
        name        : '/' + window.namespace + '/reconfiguration/gettableextents',
        serviceType : 'user_interface/GetTableExtents'
    }); 

    var request = new ros.ServiceRequest();

    table_objects = []

    console.log(service);

    service.callService(request, function(response){
        console.log('response: ' + response);
        table_x = response.x;
        table_y = response.y;
        table_xext = response.xextents;
        table_yext = response.yextents;
        goal_x = response.goalx;
        goal_y = response.goaly;
        goal_radius = response.goalradius;

        width = 2*table_xext*scale;
        height = 2*table_yext*scale;

        offset_x = scale*2*table_x;
        offset_y = 0;
        
        canvas_offset_x = -1*scale*(table_x-table_xext);
        canvas_offset_y = -1*scale*(table_y-table_yext);

        table_xpos = ScaleXForward(table_x+table_xext);
        table_ypos = ScaleYForward(table_y-table_yext);

        console.log("Canvas_offsets: (" + canvas_offset_x + "," + canvas_offset_y + ")");
        console.log("Offsets: (" + offset_x + "," + offset_y + ")");

        drawTable();
        drawGoal();
        getScene(true);
    });
}

function ScaleXForward(x){ return ((-scale*x) + offset_x + canvas_offset_x); }

function ScaleYForward(y){ return ((scale*y) + offset_y + canvas_offset_y); }

function ScaleXBack(x){ return (x - offset_x - canvas_offset_x)/(-1*scale);}

function ScaleYBack(y) { return (y - offset_y - canvas_offset_y)/scale; }

function ScaleForward(x,y){return (new Position(ScaleXForward(x),ScaleYForward(y)));}

function ScaleBackward(x,y){ return (new Position(ScaleXBack(x),ScaleYBack(y)));}

/***************************************************************************************************************/    

function Position(x, y)
{
    this.x = x;
    this.y = y;
}


function ObjectHerb(id, type, start_location, is_goal, is_blocking, xextent, yextent, rot, off)
{
    this.id = id;
    this.type = type;
    this.start_location = start_location;
    this.location_list = new Array();
    this.location_list[0] = new Position(start_location.x, start_location.y);
    this.scaled_location_list = new Array();
    this.scaled_location_list[0] = ScaleForward(start_location.x, start_location.y);
    this.is_goal = is_goal;
    this.is_blocking = is_blocking;
    this.xext = xextent;
    this.yext = yextent;
    this.rot = rot;
    this.off = off;
}

/***************************************************************************************************************/    
function drawTable()
{
    table = paper
        .rect(table_xpos, table_ypos, width, height)
        .attr("fill", "#e1e1e1")
        .attr({stroke: '#7e7b7b', "stroke-width":5})
    ;

    console.log("Creating table: " + "at (" + table_xpos + "," + table_ypos + ") and with dimensions: (" + width + "," + height + ")");
    console.log(table);
}

function drawGoal()
{ 
    var x_pos = ScaleXForward(goal_x);
    var y_pos = ScaleYForward(goal_y);
    var g_radius = scale*goal_radius;

    var cylinder = paper.circle(width - x_pos - g_radius/2, y_pos, g_radius-stroke)
        .scale(false)
        .attr("stroke-width", stroke)
        .attr({stroke: '#00b200'})
    ;
    console.log(width);

    return cylinder;
}    

function drawObject(o, init)
{   
    if (o.type=="target"){
        box_xext = o.xext;
        box_yext = o.yext;
        draw_object = drawBox(o, o.start_location.x, o.start_location.y, o.rot, init);
    }
    else if (o.type == "fuze_bottle"){
        fuze_ext = o.xext;
        draw_object = drawFuzeBottle(o.start_location.x, o.start_location.y, init);
    }
    else if (o.type == "plastic_glass"){
        glass_ext = o.xext;
        draw_object = drawGlass(o.start_location.x, o.start_location.y, init);
    }
    else if (o.type == "pop_tarts"){
        pop_xext = o.xext;
        pop_yext = o.yext;
        draw_object = drawBox(o, o.start_location.x, o.start_location.y, o.rot, init);
    }
    else {
        hand_xext = o.xext;
        hand_yext = o.yext;
        draw_object = drawHand(o.start_location.x, o.start_location.y, o.rot, o.off, init);
    }
    draw_object.data("herb_obj", o);
    return draw_object
}


function drawBox(o, x, y, rot, init)
{
    var x_pos = ScaleXForward(x+box_xext*.525);
    var y_pos = ScaleYForward(y-1.25*box_yext*.525);
    var b_width = scale*box_xext*1.5;
    var b_height = scale*box_yext*1.5;
    var deg = (rot/Math.PI)*180;
    var center_x = (width - x_pos - (b_width-2*stroke)/2);
    var center_y = (y_pos + (b_height-2*stroke)/2);

    if (init == true) {
        var fill = "#00b200";
        if (o.type == "pop_tarts") {
            var fill = "#000000";
        }

        var box = paper
            .rect(width - x_pos - (b_width-2*stroke), y_pos, b_width-2*stroke, b_height-2*stroke)
            .rotate(-deg, center_x, center_y)
            .attr("fill", fill)
            .scale(false)
            .attr("stroke-width", stroke)
        ;

        box.attr("stroke", fill);
    }
    else {
        var box = table_objects.shift();
        box.transform("");
        box.attr({x : width - x_pos - (b_width-2*stroke), y : y_pos, transform : "r" + (-deg)});
    }

    return box;
}

function drawHand(x, y, rot, off, init)
{
    hand_x = x;
    hand_y = y;

    var x_pos = ScaleXForward(x-hand_xext);
    var y_pos = ScaleYForward(y-1.75*hand_yext);

    var h_width = scale*hand_xext*2;
    var h_height = scale*hand_yext*2;
    var deg = (rot/Math.PI)*180;

    if (init == true) {
        var herb = paper.image("/static/img/bh280.png",x_pos + 24, y_pos, h_width, h_height);
        herb.rotate(-deg, x_pos + 24  + h_width/2, y_pos + h_height);
    }
    else {
        var herb = table_objects.shift();
        console.log(herb.getBBox().x);
        console.log(x_pos);
        herb.transform("");
        herb.attr({x : x_pos + 24, y : y_pos});
        herb.rotate(-deg, x_pos + 24 + h_width/2, y_pos + h_height);
    }

    return herb;
}

function drawFuzeBottle(x, y, init)
{        
    var x_pos = ScaleXForward(x - fuze_ext);
    var y_pos = ScaleYForward(y);
    var f_radius = scale*fuze_ext;

    if (init == true) {
        var fuze = paper.circle(x_pos + width/3, y_pos, f_radius)
            .attr({fill:"#000000"})
            .scale(false)
        ;
    }

    else {
        var fuze = table_objects.shift();
        fuze.attr({cx : x_pos + width/3, cy : y_pos});
    }

    return fuze;
}

function drawGlass(x, y, init)
{        
    var x_pos = ScaleXForward(x - glass_ext);
    var y_pos = ScaleYForward(y);
    var f_radius = scale*glass_ext;
    
    if (init == true) {
        var glass = paper.circle(x_pos + width/3, y_pos, f_radius)
            .attr({fill:"#000000"})
            .scale(false)
        ;
    }

    else {
        var glass = table_objects.shift();
        glass.attr({cx : x_pos + width/3, cy : y_pos});
    }

    return glass;
}

function drawKeys() {
    var canvas = document.getElementById('canvas'),
    ctx = canvas.getContext('2d');
    canvas.width = 880;
    canvas.height = window.innerHeight;
    var rect_x = (canvas.width - 314)/2 + 300;
    ctx.textAlign="center";
    ctx.font="20px Arial"; 
    if (validMove == "False") {
        ctx.fillStyle = "#FF0000";
        ctx.fillRect(rect_x,30,200,65);

        ctx.fillStyle = "#000000";
        ctx.fillText("Invalid Move",rect_x+100,70);
    }
    else {
        ctx.fillStyle = "#0AD400";
        ctx.fillRect(rect_x,30,200,65);

        ctx.fillStyle = "#000000";
        ctx.fillText("Valid Move",rect_x+100,70)
    }
    var img = new Image();
    img.src = "/static/img/key_mapping.png";
    var imgW = 360;
    var imgH = imgW*0.817;
    var imgX = rect_x - imgW/2 + 100;
    ctx.drawImage(img, imgX, 105, imgW, imgH);
}

/***************************************************************************************************************/    
function regenerateScene()
{
    getScene(false);
}

function getScene(initialize)
{
    var service = new ros.Service({
        name        : '/' + window.namespace + '/reconfiguration/getobjects',
        serviceType : 'user_interface/GetObjectList'
    });

    console.log(service);
    var request = new ros.ServiceRequest();
    var d = new Date();
    console.log('Time Object List Recieved: ' + d);
    console.log(request);

    service.callService(request, function(response)
                        {
                            drawKeys();
                            console.log(response);
                            console.log('Creating objects.');
                            for (var i=0; i<response.num_objects;i++)
                            {
                                var o_temp = response.objects[i];
                                console.log(o_temp.x, o_temp.y);
                                
                                if(o_temp.type == "bh280" && (keyboard_input == "tleft" || keyboard_input == "tright"))
                                {
                                    var start_pos =  new Position(hand_x, hand_y);
                                }
                                else
                                {
                                    var start_pos =  new Position(o_temp.x, o_temp.y);
                                }

                                if(o_temp.type == "target" && initialize == true)
                                {
                                    box_start_x = o_temp.x;
                                    box_start_y = o_temp.y;
                                }

                                var o = new ObjectHerb(o_temp.id, o_temp.type, start_pos, o_temp.isgoal, o_temp.isblocking, o_temp.xextent, o_temp.yextent, o_temp.rot, o_temp.off);
                                var draw_obj = drawObject(o, initialize);

                                table_objects.push(draw_obj);

                                if (sceneNum == 0 && initialize == true) { $('#practiceModal').modal('show'); }
                                else if (response.in_goal == true) { 
                                    if (sceneNum == 1) {  $('#studyModal').modal('show'); }
                                    else if (sceneNum == 15) { $('#surveyModal').modal('show'); } 
                                    else { $('#inGoalModal').modal('show'); } 
                                    inGoal = true 
                                }
                            }   
                        });      
}
/***************************************************************************************************************/    
function Next_Scene (button) 
{
    sceneNum++;
    console.log(sceneNum);
    console.log("Loading Next Scene.");

    var service = new ros.Service({
        name        : '/' + window.namespace + '/reconfiguration/nextscene',
        serviceType : 'user_interface/NextScene'
    });

    var request = new ros.ServiceRequest();
    request.sceneNum = sceneNum;

    service.callService(request, function(response)
                        {
                            if (sceneNum > 15) { 
                                window.location.href = "survey.html";
                            }
                            else {
                                paper.clear();
                                initializeScene();
                                if (sceneNum < 2){
                                    document.getElementById('brand').text='Push Planning User Study: Practice Scene ' + (sceneNum+1) + '/2';
                                }
                                else {
                                    document.getElementById('brand').text='Push Planning User Study: Scene ' + (sceneNum-1) + '/14';
                                }
                                inGoal = false;
                            }
                        });
}

$('#Prev_Scene').click(function () 
                       {
                           console.log("Loading Previous Scene.");

                           var service = new ros.Service({
                               name        : '/' + window.namespace + '/reconfiguration/nextscene',
                               serviceType : 'user_interface/NextScene'
                           });

                           var request = new ros.ServiceRequest();
                           sceneNum--;
                           request.sceneNum = sceneNum;

                           service.callService(request, function(response)
                                               {
                                                   paper.clear();
                                                   initializeScene();
                                               }); 
                       });

function Reset_Scene (button) 
{
    console.log("Resetting scene.");

    var service = new ros.Service({
        name        : '/' + window.namespace + '/reconfiguration/nextscene',
        serviceType : 'user_interface/NextScene'
    });

    var request = new ros.ServiceRequest();
    request.sceneNum = sceneNum;

    service.callService(request, function(response)
                        {
                            paper.clear();
                            initializeScene();
                        }); 
}



window.addEventListener("keydown", function(e) {
    // space and arrow keys
    if([32, 37, 38, 39, 40].indexOf(e.keyCode) > -1) {
        e.preventDefault();
    }
}, false);

