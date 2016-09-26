// surveyhandler.js:
// -catches submit button click on the survey page
// -stops from going to the page the submit button linked to
//  if any of the inputs is empty
jQuery(function ($) {
    function demandCompletion(e){
        e.preventDefault();
        $(".text-danger").removeClass('hide');
    }
    //submit the form only if it's complete
    $('#survey').submit(function (e) {
        //check multiple-choice
        if (!$("input[name=1]:checked").val()) demandCompletion(e);
        if (!$("input[name=5]:checked").val()) demandCompletion(e);
	if (!$("input[name=6]:checked").val()) demandCompletion(e);
	if (!$("input[name=7]:checked").val()) demandCompletion(e);

        //check free response
        if ($(".fr2").val()=='') demandCompletion(e);
    })
})
