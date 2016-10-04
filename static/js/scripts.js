$(document).ready(function(){
	$('.vote').click(function(){
		var vid = $(this).attr('post_id')
		if($(this).hasClass("vote-up")){
			// user voted on the up arrow
			var voteType = 1;
		}else{
			// use must have voted on teh down arrow. Vote down
			var voteType = -1;
		}
		$.ajax({
			url: "/process_vote",
			type: "post",
			data: {vid:vid, voteType:voteType},
			success: function(result){
				console.log(result)
			}
		});


	});
});