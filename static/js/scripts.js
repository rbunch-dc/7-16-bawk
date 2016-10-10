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
				if(result.message == 'voteChanged'){
					// The user's vote was updated by python. Update our field ni HTML
					$("div[up-down-id='" + vid + "']").html(result.vote_total)
				}else if(result.message == 'alreadyVoted'){
					// THe users's vote was not updated for whatever reason. Let them Know
					$("div[up-down-id='" + vid + "']").html('You have already voted on this bawk!')
				}
				console.log(result)
			}
		});


	});
});