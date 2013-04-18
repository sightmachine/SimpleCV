(function($) {
// BEGIN Before Page Ready



// END Before Page Ready
// BEGIN After Page Ready
$(document).ready(function() {

    /* Init accordions */
    $('#Accordion').accordion({
        'collapsible':true
    });

    /* Fix right column borders */
    $('.callout').first().css({'margin-top':0});
    $('.callout').last().css({'margin-bottom':0, 'padding-bottom':0, 'border-bottom':0});

});
// END After Page Ready
})(jQuery);
