// Widget-specific code

// Set a variable to check to see if this script is loaded
var BP_FORM_COMPLETE_LOADED = true;

// Set the defaults if they haven't been set yet
if (typeof BP_SEARCH_SERVER === 'undefined') {
  var BP_SEARCH_SERVER = "http://bioportal.bioontology.org";
}
if (typeof BP_SITE === 'undefined') {
  var BP_SITE = "BioPortal";
}
if (typeof BP_ORG === 'undefined') {
  var BP_ORG = "NCBO";
}
if (typeof BP_ONTOLOGIES === 'undefined') {
  var BP_ONTOLOGIES = "";
}

var BP_ORG_SITE = (BP_ORG == "") ? BP_SITE : BP_ORG + " " + BP_SITE;



jQuery(document).ready(function(){
  // Install any CSS we need (check to make sure it hasn't been loaded)
  // fire start event
  formComplete_setup_functions();
});

function formComplete_formatItem(row) {
  var input = this.extraParams.input;
  var specials = new RegExp("[.*+?|()\\[\\]{}\\\\]", "g"); // .*+?|()[]{}\
  var keywords = jQuery(input).val().replace(specials, "\\$&").split(' ').join('|');
  var regex = new RegExp( '(' + keywords + ')', 'gi' );
  var result = "";
  var ontology_id;
  var term_name_width = "350px";

  // Get ontology id and other parameters
  var classes = jQuery(input).attr('class').split(" ");
  jQuery(classes).each(function() {
    if (this.indexOf("bp_form_complete") === 0) {
      var values = this.split("-");
      ontology_id = values[1];
    }
  });
  var BP_include_definitions = jQuery(input).attr("data-bp_include_definitions");


  // TODO: Add formatting for different object types: class, property, individual?


  // Set wider term name column
  if (BP_include_definitions === "true") {
    term_name_width = "150px";
  } else if (ontology_id == "all") {
    term_name_width = "320px";
  }

  // Results
  var result_type = row[2];
  var result_term = row[0];
  var result_ont_version = row[3];
  var result_uri = row[4];

  // row[7] is the ontology_id, only included when searching multiple ontologies
  if (ontology_id !== "all") {
    if (BP_include_definitions === "true") {
      result += definitionMarkup(result_ont_version, result_uri);
    }

    result += "<div class='result_term' style='width: "+term_name_width+";'>" + result_term.replace(regex, "<b><span class='result_term_highlight'>$1</span></b>") + "</div>";

    result += "<div class='result_type' style='overflow: hidden;'>" + result_type + "</div>";
  } else {
    // Results
    var result_ont = row[7];
    var result_def = row[9];

    result += "<div class='result_term' style='width: "+term_name_width+";'>" + result_term.replace(regex, "<b><span class='result_term_highlight'>$1</span></b>") + "</div>"

    if (BP_include_definitions === "true") {
      result += definitionMarkup(result_ont_version, result_uri);
    }

    result += "<div>" + " <div class='result_type'>" + result_type + "</div><div class='result_ontology' style='overflow: hidden;'>" + truncateText(result_ont, 35) + "</div></div>";
  }

  return result;
}

function definitionMarkup(ont, concept) {
  return "<div class='result_definition'>retreiving definitions...<a class='get_definition_via_ajax' href='"+BP_SEARCH_SERVER+"/ajax/json_term?callback=?&ontologyid="+ont+"&conceptid="+encodeURIComponent(concept)+"'></a></div>";
}

function formComplete_setup_functions() {
  jQuery("input[class*='bp_form_complete']").each(function(){
    var classes = this.className.split(" ");
    var values;
    var ontology_id;
    var target_property;

    var BP_search_branch = jQuery(this).attr("data-bp_search_branch");
    if (typeof BP_search_branch === "undefined") {
      BP_search_branch = "";
    }

    var BP_include_definitions = jQuery(this).attr("data-bp_include_definitions");
    if (typeof BP_include_definitions === "undefined") {
      BP_include_definitions = false;
    }

    // Setup polling if we need definitions
    if (BP_include_definitions) {
      getWidgetAjaxContent();
    }

    var BP_objecttypes = jQuery(this).attr("data-bp_objecttypes");
    if (typeof BP_objecttypes === "undefined") {
      BP_objecttypes = "";
    }

    // Find the 'bp_form_complete-{ontologyId,...}-{property}' values
    // in the class attribute(s)
    jQuery(classes).each(function() {
      if (this.indexOf("bp_form_complete") === 0) {
        values = this.split("-");
        ontology_id = values[1]; // Could be CSV (see wiki documentation)
        target_property = values[2];
      }
    });

    if (ontology_id == "all") { // Doesn't handle CSV?
    	ontology_id = "";
    }

    var extra_params = {
  		input: this,
  		target_property: target_property,
  		subtreerootconceptid: encodeURIComponent(BP_search_branch),
  		objecttypes: BP_objecttypes,
  		id: BP_ONTOLOGIES // not 'ontology_id', see below...
    };

    var result_width = 450;
    // Add space for definition
    if (BP_include_definitions) {
      result_width += 275;
    }
    // Add space for ontology name
    if (ontology_id === "") {
      result_width += 200;
    }

    // see "public/javascripts/JqueryPlugins/autocomplete/crossdomain_autocomplete.js"
    jQuery(this).bioportal_autocomplete(
		  BP_SEARCH_SERVER + "/search/json_search/" + ontology_id,
		  {
	        extraParams: extra_params,
	        lineSeparator: "~!~",
	        matchSubset: 0,
	        minChars: 3,
	        maxItemsToShow: 20,
	        width: result_width,
	        onItemSelect: bpFormSelect,
	        footer: '<div style="color: grey; font-size: 8pt; font-family: Verdana; padding: .8em .5em .3em;">Results provided by <a style="color: grey;" href="' + BP_SEARCH_SERVER + '">' + BP_ORG_SITE + '</a></div>',
	        formatItem: formComplete_formatItem
	    }
    );

    var html = "";
    if (document.getElementById(jQuery(this).attr('name') + "_bioportal_concept_id") == null)
      html += "<input type='hidden' id='" + jQuery(this).attr('name') + "_bioportal_concept_id'>";
    if (document.getElementById(jQuery(this).attr('name') + "_bioportal_ontology_id") == null)
      html += "<input type='hidden' id='" + jQuery(this).attr('name') + "_bioportal_ontology_id'>";
    if (document.getElementById(jQuery(this).attr('name') + "_bioportal_full_id") == null)
      html += "<input type='hidden' id='" + jQuery(this).attr('name') + "_bioportal_full_id'>";
    if (document.getElementById(jQuery(this).attr('name') + "_bioportal_preferred_name") == null)
      html += "<input type='hidden' id='" + jQuery(this).attr('name') + "_bioportal_preferred_name'>";

    jQuery(this).after(html);
  });
}

// Sets a hidden form value that records the concept id when a concept is chosen in the jump to
// This is a workaround because the default autocomplete search method cannot distinguish between two
// concepts that have the same preferred name but different ids.
function bpFormSelect(li) {
  var input = this.extraParams.input;
  switch (this.extraParams.target_property) {
    case "uri":
      jQuery(input).val(li.extra[3])
      break;
    case "shortid":
      jQuery(input).val(li.extra[0])
      break;
    case "name":
      jQuery(input).val(li.extra[4])
      break;
  }

  jQuery("#" + jQuery(input).attr('name') + "_bioportal_concept_id").val(li.extra[0]);
  jQuery("#" + jQuery(input).attr('name') + "_bioportal_ontology_id").val(li.extra[2]);
  jQuery("#" + jQuery(input).attr('name') + "_bioportal_full_id").val(li.extra[3]);
  jQuery("#" + jQuery(input).attr('name') + "_bioportal_preferred_name").val(li.extra[4]);
}

// Poll for potential definitions returned with results
function getWidgetAjaxContent() {
  // Look for anchors with a get_via_ajax class and replace the parent with the resulting ajax call
  $(".get_definition_via_ajax").each(function(){
    var def_link = $(this);
    if (typeof def_link.attr("getting_content") === 'undefined') {
      def_link.attr("getting_content", true);
      $.getJSON(def_link.attr("href"), function(data){
        var definition = (typeof data.id === 'undefined') ? "" : data.id;
        def_link.parent().html(truncateText(decodeURIComponent(definition.replace(/\+/g, " "))));
      });
    }
  });
  setTimeout(getWidgetAjaxContent, 100);
}

function truncateText(text, max_length) {
  if (typeof max_length === 'undefined' || max_length == "") {
    max_length = 70;
  }

  var more = '...';

  var content_length = $.trim(text).length;
  if (content_length <= max_length)
    return text;  // bail early if not overlong

  var actual_max_length = max_length - more.length;
  var truncated_node = jQuery("<div>");
  var full_node = jQuery("<div>").html(text).hide();

  text = text.replace(/^ /, '');  // node had trailing whitespace.

  var text_short = text.slice(0, max_length);

  // Ensure HTML entities are encoded
  // http://debuggable.com/posts/encode-html-entities-with-jquery:480f4dd6-13cc-4ce9-8071-4710cbdd56cb
  text_short = $('<div/>').text(text_short).html();

  var other_text = text.slice(max_length, text.length);

  text_short += "<span class='expand_icon'><b>"+more+"</b></span>";
  text_short += "<span class='long_text'>" + other_text + "</span>";
  return text_short;
}