$(function(){
    function toggle_contents(){
        // get select button list
        items = $("#select-buttons [data-id]")
        for (var i = 0; i < items.length; i += 1) {
            // get button id
            data_id = $(items[i]).attr('data-id')
            // console.log(data_id)
            if ($(items[i]).hasClass('active')){
                // show contents
                // console.log("show")
                $('[data-content-id='+data_id+']').show()
            } else {
                // hide contents
                // console.log("hide")
                $('[data-content-id='+data_id+']').hide()
            }
        }
    }
    
    $("#search").on("click", function(){
        toggle_contents()
    })
    
    $(".intro-social-buttons .btn").on("click", function(){
        if($(this).hasClass("active")) {
            $(this).removeClass("active")
        } else {
            $(this).addClass("active")
        }
    })
    
    //toggle_contents()
});