description = "axis plotter";
vendor = "adsk";
legal = "Copyright (C) 2012-2023 by Autodesk, Inc.";
certificationLevel = 2;
minimumRevision = 45917;

longDescription = "Plot C axis into HTML.";

extension = "bcp";
programNameIsInteger = true;
setCodePage("ascii");

capabilities = CAPABILITY_MILLING | CAPABILITY_MACHINE_SIMULATION;
tolerance = spatial(0.002, MM);

minimumChordLength = spatial(0.25, MM);
minimumCircularRadius = spatial(0.01, MM);
maximumCircularRadius = spatial(1000, MM);
minimumCircularSweep = toRad(0.01);
maximumCircularSweep = toRad(180);
allowHelicalMoves = true;
allowedCircularPlanes = 0; // allow any circular motion
highFeedrate = (unit == IN) ? 500 : 5000;
probeMultipleFeatures = true;

var valFormat = createFormat({decimals:3, forceDecimal:true, force: true, scale: 0.1 /** CM for Fusion API */});
var mapToWCS = false;

function onOpen() {
}

function onSection() {

  if (currentSection.getTool().type != TOOL_MILLING_END_BALL) { 
    //error('Only ball nose tools are supported');
  }
}


let points = '';

// Assuming the point is an array of three numbers [x, y, z]
// and the vector is an array of three numbers [vx, vy, vz]
// and the distance is a positive number
function movePointByDistance(point, vector, distance) {
    // Calculate the magnitude of the vector
    let magnitude = Math.sqrt(vector[0] * vector[0] + vector[1] * vector[1] + vector[2] * vector[2]);
    // If the magnitude is zero, return the original point
    if (magnitude === 0) {
      return point;
    }
    // Normalize the vector by dividing each component by the magnitude
    let normalized = [vector[0] / magnitude, vector[1] / magnitude, vector[2] / magnitude];
    // Multiply each component of the normalized vector by the distance
    let scaled = [normalized[0] * distance, normalized[1] * distance, normalized[2] * distance];
    // Add the scaled components to the point coordinates
    point[0] += scaled[0];
    point[1] += scaled[1];
    point[2] += scaled[2];
    
    if (points != '') {
      points += ','
    } 
    points += valFormat.format(point[0]) + ',' + valFormat.format(point[1]) + ',' +  valFormat.format(point[2])    

  }

function onRapid5D(x, y, z, a, b, c) {
  movePointByDistance([x,y,z], [a,b,c], tool.diameter/2);
}

function onLinear(x, y, z, feed) {
  movePointByDistance([x,y,z], [currentSection.wcsPlane.forward.x, currentSection.wcsPlane.forward.y, currentSection.wcsPlane.forward.z], tool.diameter/2);
}


function onRapid(x, y, z) {
  movePointByDistance([x,y,z],  [currentSection.wcsPlane.forward.x, currentSection.wcsPlane.forward.y, currentSection.wcsPlane.forward.z], tool.diameter/2);
}

function onLinear5D(x, y, z, a, b, c, feed, feedMode) {
  movePointByDistance([x,y,z], [a,b,c], tool.diameter/2);
}


function onClose(){
    writeln(points)
}