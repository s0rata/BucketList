// Function to show list of wishes
function GetWishes(_page){
    var offset = (_page - 1) * 2;
    $.ajax({
        url: '/getWish',
        type: 'POST',
        data: {
            offset: 0
        },
        success: function(res){
            // Parse the JSON respond
            var wishObj = JSON.parse(res);
            $('#ulist').empty();
            // Append to the template
            $('#listTemplate').tmpl(wishObj[0]).appendTo('#ulist');
            // console.log(res);
            var total = wishObj[1]['total'];
            var itemsPerPage = 2;

            var pageCount = total/itemsPerPage;
            var pageRem = total%itemsPerPage;
            // console.log(pageCount,pageRem);
            if(pageRem !=0 ){
                pageCount = Math.floor(pageCount)+1;
            }

            // Empty pagination
            $('.pagination').empty();
            var pageStart = $('#hdnStart').val();
            var pageEnd = $('#hdnEnd').val();

            // Add previous link when page is greater than 5
            if (pageStart > 5) {
                // console.log('mhere', pageStart);
                var aPrev = $('<a/>').attr({
                        'href': '#'
                    }, {
                        'aria-label': 'Previous'
                    })
                    .append($('<span/>').attr('aria-hidden', 'true').html('&laquo;'));
 
                $(aPrev).click(function() {
                    $('#hdnStart').val(Number(pageStart) - 5);
                    $('#hdnEnd').val(Number(pageStart) - 5 + 4);
                    GetWishes(Number(pageStart) - 5);
                });
 
                var prevLink = $('<li/>').append(aPrev);
                $('.pagination').append(prevLink);
            }

            // Loop for creating pagination number
            for (var i = Number(pageStart); i <= Number(pageEnd); i++) {
                if (i > pageCount) {
                    // console.log('break');
                    break;
                }

                var aPage = $('<a/>').attr('href', "#").text(i);
                $(aPage).click(function(i) {
                    // return function() {
                    //     GetWishes(i);
                    // }
                    console.log('click', i);
                    GetWishes(i);
                });
                var page = $('<li/>').append(aPage);
 
                if ((_page) == i) {
                    // console.log('page');
                    $(page).attr('class', 'active');

                }
                // console.log('mhere2');
                 $('.pagination').append(page);
            }

            // Add next link when page is greater than 5
            if ((Number(pageStart) + 5) <= pageCount) {
                var nextLink = $('<li/>').append($('<a/>').attr({
                        'href': '#'
                    }, {
                        'aria-label': 'Next'
                    })
                    .append($('<span/>').attr('aria-hidden', 'true').html('&raquo;').click(function() {
                        $('#hdnStart').val(Number(pageStart) + 5);
                        $('#hdnEnd').val(Number(pageStart) + 5 + 4);
                        GetWishes(Number(pageStart) + 5);
 
                    })));
                $('.pagination').append(nextLink);
            }
            
        },
        error: function(error){
            console.log(error);
        }
    });
}

//Function for update button
$(function(){
    GetWishes(1);
    $('#btnUpdate').click(function() {
        // console.log('success');
        $.ajax({
            url: '/updateWish',
            data: {
                title: $('#editTitle').val(),
                description: $('#editDescription').val(),
                id: localStorage.getItem('editId'),
                filePath: $('#imgUpload').attr('src'),
                isPrivate: $('#chkPrivate').is(':checked')? 1:0,
                isDone: $('#chkDone').is(':checked')? 1:0
            },
            type: 'POST',
            success: function(res) {
                $('#editModal').modal('hide');
                 console.log('Updated!', res);
                // Re populate the grid
                GetWishes();
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});

// Function for edit button
function edit(elm) {
    localStorage.setItem('editId',$(elm).attr('data-id'));
    $.ajax({
        url: '/getWishById',
        data: {
            id: $(elm).attr('data-id')
        },
        type: 'POST',
        success: function(res) {
            var data = JSON.parse(res);
            console.log(data);
            $('#editTitle').val(data[0]['Title']);
            $('#editDescription').val(data[0]['Description']);
            $('#imgUpload').attr('src', data[0]['FilePath']);
            if (data[0]['Private'] == 1){
                $('#chkPrivate').attr('checked', 'checked');
            }
            if (data[0]['Done'] == 1){
                $('#chkDone').attr('checked','checked');
            }
            $('#editModal').modal();
        },
        error: function(error) {
            console.log(error);
        }
    });
}

// Function for trash button
function confirmDelete(elem){
    localStorage.setItem('deleteId', $(elem).attr('data-id'));
    $('#deleteModal').modal();
}

// Function for delete button
function Delete(){
    $.ajax({
        url: '/deleteWish',
        data: {
            id: localStorage.getItem('deleteId')
        },
        type: 'POST',
        success: function(res){
            var result = JSON.parse(res);
            if (result.status = 'Ok'){
                $("#deleteModal").modal('hide');

            }else{
                alert(result.status);
            }
            GetWishes();
            console.log("Deleted!");
        },
        error: function(error) {
            console.log(error);
        }
    });
}

// Fileupload 
$(function() {
    // console.log('fileupload');
    $('#fileupload').fileupload({
        url: '/upload',
        dataType: 'json',
        add: function(e, data) {
            data.submit();
        },
        success: function(response, status) {
            console.log(response);
            var filePath = '/static/Uploads/' + response.filename;
            $('#imgUpload').attr('src', filePath);
            $('#filePath').val(filePath);
            
        },
        error: function(error) {
            console.log(error);
        }
    });
})