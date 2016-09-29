$(document).on('click', '[id^="btn_"]', function() {
	var spId = $(this).attr('id').split('_')[1];
	$.ajax({
		url: '/addUpdateLikes',
		method: 'POST',
		data: {
			wish: $(this).attr('id').split('_')[1],
			like: 1
		},
		success: function(response){
			var data = JSON.parse(response);
			// var id = '#btn_' + data['Like'];
			// $(id).removeClass("btn-primary").addClass("btn-success");
			if (data.LikeStatus == 1){
				$('#span_' + spId).html('&nbsp;You & ' + (Number(data.Total) - 1 + ' Others'));
			} else {
				$('#span_' + spId).html('&nbsp;You & ' + data.Total + 'like(s)');
			}
			console.log(response);
			
		},
		error: function(error){
			console.log(error);
		}
	});
});

$(function(){
	$.ajax({
		url: '/getAllWishes',
		type: 'GET',
		success: function(res){
			// console.log(res);
			var data = JSON.parse(res);
			var itemsPerRow = 0;
			var div = $('<div>').attr('class', 'row');
			for (var i = 0; i < data.length; i++){
				if (itemsPerRow < 3){
					if (i == data.length - 1){
						div.append(createThumb(data[i].Id, data[i].Title, data[i].Description, data[i].FilePath, data[i].Like));
					} else {
						div.append(createThumb(data[i].Id, data[i].Title, data[i].Description, data[i].FilePath, data[i].Like));
						itemsPerRow++;
					}
				} else {
					$('.well').append(div);
					div = $('<div>').attr('class', 'row');
					div.append(createThumb(data[i].Id, data[i].Title, data[i].Description, data[i].FilePath, data[i].Like));
					if ( i == data.length -1){
						$('.well').append(div);
					}
					itemsPerRow = 1;
				}
			}
		},
		error: function(error){
			console.log(error);
		}
	});
})

function createThumb(id,title, desc, filepath, like, hasLiked) {
   
    var mainDiv = $('<div>').attr('class', 'col-sm-4 col-md-4');
   
    var thumbNail = $('<div>').attr('class', 'thumbnail');
                                     
    var img = $('<img>').attr({
        'src': filepath,
        'data-holder-rendered': true,
        'style': 'height: 150px; width: 150px; display: block'
    });
   
    var caption = $('<div>').attr('class', 'caption');
   
    var title = $('<h3>').text(title);
   
    var desc = $('<p>').text(desc);
 
 
    var p = $('<p>');
   
    var btn = $('<button>').attr({
        'id': 'btn_' + id, 
        'type': 'button',
        'class': 'btn btn-primary btn-sm'
    });
   
    var span = $('<span>').attr({
        'class': 'glyphicon glyphicon-thumbs-up',
        'aria-hidden': 'true'
    });
	
	var likeSpan = $('<span>').attr({'aria-hidden': 'true', 'id': 'span_'+id}).html('&nbsp;'+like+' like(s)');

	if (hasLiked == 1) {
	    likeSpan.html('&nbsp;You & ' + (Number(like) - 1) + ' Others');
	} else {
	    likeSpan.html('&nbsp;' + like + ' like(s)');
	}

    p.append(btn.append(span));
    p.append(likeSpan);

    caption.append(title);
    caption.append(desc);
    caption.append(p);
 
    thumbNail.append(img);
    thumbNail.append(caption);
    mainDiv.append(thumbNail);
    return mainDiv;
 
 
}
