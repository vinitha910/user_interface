var imgID = 0;

function changeImage(nextImg) {
    var rotator = document.getElementById('ui-image');
    var imgDir = '/static/img/';

    var images = ['slide1.png', 'slide2.png', 'slide3.png', 'slide4.png', 'slide5.png', 'slide6.png']

    if (nextImg == true) {
	imgID++;
    }
    else {
	imgID--;
    }

    var len = images.length;
    if (imgID < 0) {
	location.href = '/'
    }
    else if (imgID < len) {
	rotator.src = imgDir + images[imgID];
    }
    else {
	location.href = '/index.html'
    }
}

    
