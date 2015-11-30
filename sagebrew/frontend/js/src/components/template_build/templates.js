var Handlebars = require("handlebars");
 exports["position_image_radio"] = Handlebars.template({"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : {}, alias2=helpers.helperMissing, alias3="function", alias4=container.escapeExpression;

  return "<div class=\"col-xs-12 col-sm-4\">\n    <div class=\"radio-image-selector\">\n        <h4 class=\"sb-profile-not-friend-header\">"
    + alias4(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"name","hash":{},"data":data}) : helper)))
    + "</h4>\n        <div class=\"row radio-image-selector-image-wrapper\">\n            <img class=\"radio-image-selector-image\" src=\""
    + alias4(((helper = (helper = helpers.image_path || (depth0 != null ? depth0.image_path : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"image_path","hash":{},"data":data}) : helper)))
    + "\">\n        </div>\n    </div>\n</div>";
},"useData":true});