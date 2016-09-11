var testData = {
  "lines": [{
            "id": "some_unique_id",
            "blat": 37.297227,
            "blon": -122.012742,
            "elat": 37.299227,
            "elon": -122.012742,
            "sides": "W",
            "address": "Hello",
            "type": "meter",
            "rate": 3,
            "availabilities": [{
              "start_day": "MON",
              "end_day": "FRI",
              "start_time": "0800A",
              "end_time": "1000P",
              "limit": 3
            }]
  }, 
  {
    "id": "some_unique_id",
    "blat": 34.4175,
    "blon": 3,
    "elat": 173,
    "elon": 3,
    "sides": "W",
    "address": "Hello",
    "type": "zone",
    "availabilities": [{
      "start_day": "MON",
      "end_day": "FRI",
      "start_time": "0800A",
      "end_time": "1000P",
      "limit": 3
    }]
  }
  ]
}

function initMap() {
  var philly = {lat: 39.9525839, lng: -75.16522150000003};
  var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 10,
    center: philly
  });

  var contentString = 'Ayy lmao';
  var infowindow = new google.maps.InfoWindow({
    content: contentString,
    maxWidth: 200
  });

  var marker = new google.maps.Marker({
    position: philly,
    map: map,
    title: 'philly (Ayers Rock)'
  });

  marker.addListener('click', function() {
    infowindow.open(map, marker);
  });

  // Enter address
  document.getElementById('btn').onclick = function() {
    var geocoder = new google.maps.Geocoder();

    var search = document.getElementById('address').value;
    console.log(search);
    geocodeAddress(geocoder, map);
    map.setZoom(16);
  }

  // Didn't get towed
  document.getElementById('noTow').onclick = function() {
    var center = map.getCenter();
    var lat = center.lat();
    var lng = center.lng();
    addCircle(lat, lng, '#00b200', map);
    console.log(lat + " " + lng);
  }

  // Got towed
  document.getElementById('gotTowed').onclick = function() {
    var center = map.getCenter();
    var lat = center.lat();
    var lng = center.lng();
    addCircle(lat, lng, '#FF0000', map);
    console.log(lat + " " + lng);
  }

  console.log(testData);

  for (index = 0, len = testData.lines.length; index < len; ++index) {
    addLine(testData.lines[index].blat, testData.lines[index].blon, testData.lines[index].elat, 
      testData.lines[index].elon, map, testData.lines[index]);
  }
}

function generateContent(content) {
  console.log(content);
  var contentString = '<h1>Parking Info</h1>'
  + '<br><b>Parkable Sides:</b> ' + content.sides
  + '<br><b>Address:</b> ' + content.address
  + '<br><b>Type:</b> ' + content.type;

  for (index = 0, len = content.availabilities.length; index < len; ++index) {
    var avail = content.availabilities[index];
    console.log(avail);
    console.log(content.availabilities);
    var startArray = avail.start_time.split("");
    var start = startArray[0] + startArray[1] + ":" + startArray[2] + startArray[3];
    if (startArray[4] === 'P') {
      start = start + 'PM';
    } else {
      start = start + 'AM';
    }

    var endArray = avail.end_time.split("");
    var end = endArray[0] + endArray[1] + ":" + endArray[2] + endArray[3];
    if (endArray[4] == 'P') {
      end = end + 'PM';
    } else {
      end = end + 'AM';
    }
    console.log(contentString);
    contentString = contentString 
    + '<br><b>Availibility:</b> ' + avail.start_day + ' - ' + avail.end_day
    + '<br><b>Hours:</b> ' + start + ' - ' + end;
  }

  if (content.rate) {
    contentString = contentString 
    + '<br><b>Rates:</b> $' + content.rate; + 'hr';
  }
  return contentString;
}

function addCircle(latitude, long, color, map) {
  var circle = new google.maps.Circle({
            strokeColor: color,
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: color,
            fillOpacity: 0.55,
            map: map,
            center: {lat: latitude, lng: long},
            radius: 30
          });
}

function addLine(lat1, lng1, lat2, lng2, map, contentStuff) {
  var line = new google.maps.Polyline({
    path: [ {lat: lat1, lng: lng1},
      {lat: lat2, lng: lng2}
    ],
    map: map,
    geodesic: true,
    strokeColor: '#FF0000',
    strokeOpacity: 1.0,
    strokeWeight: 2
  });

  var infowindow = new google.maps.InfoWindow({
    map: map
  });  

  var content = generateContent(contentStuff);
  console.log('content' + content);

  google.maps.event.addListener(line, 'click', function(event) {         
      infowindow.setContent(content);
      infowindow.setPosition(event.latLng);
      infowindow.open(map);
  });  
}

function geocodeAddress(geocoder, resultsMap) {
  var address = document.getElementById('address').value;
  geocoder.geocode({'address': address}, function(results, status) {
    if (status === 'OK') {
      resultsMap.setCenter(results[0].geometry.location);
      myLoc = results[0].geometry.location;
      var ryan = resultsMap.getBounds();
      var NELat = ryan.getNorthEast().lat();
      var NELng = ryan.getNorthEast().lng();
      var SWLat = ryan.getSouthWest().lat();
      var SWLng = ryan.getSouthWest().lng();

      console.log(NELat + " " + NELng);
      console.log(SWLat + " " + SWLng);
      console.log(myLoc.lat() + " " + myLoc.lng());

      var marker = new google.maps.Marker({
        map: resultsMap,
        position: results[0].geometry.location
      });
    } else {
      alert('Geocode was not successful for the following reason: ' + status);
    }
  });
}