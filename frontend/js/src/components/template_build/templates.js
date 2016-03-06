var Handlebars = require("handlebars");
 exports["add_payment"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data) {
    var helper;

  return "            <div class=\"row\">\n                <div class=\"col-xs-12\">\n                    <div class=\"alert alert-warning\">\n                        "
    + container.escapeExpression(((helper = (helper = helpers.warningMsg || (depth0 != null ? depth0.warningMsg : depth0)) != null ? helper : helpers.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : {},{"name":"warningMsg","hash":{},"data":data}) : helper)))
    + "\n                    </div>\n                </div>\n            </div>\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1;

  return "<div class=\"block\">\n    <h3 class=\"block-title\">Payment Details</h3>\n    <div class=\"block-content card\">\n\n    </div>\n    <div class=\"block-content\">\n"
    + ((stack1 = helpers["if"].call(depth0 != null ? depth0 : {},(depth0 != null ? depth0.addWarning : depth0),{"name":"if","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data})) != null ? stack1 : "")
    + "        <form id=\"payment-form\" action=\"\" method=\"POST\">\n             <div class=\"row\">\n                <div class=\"col-xs-12\">\n                    <div class=\"alert alert-danger payment-errors\" hidden></div>\n                </div>\n             </div>\n            <div class=\"form-group\">\n                <label for=\"name\" class=\"control-label\">Full Name</label>\n                <input id=\"name\" class=\"input-lg form-control\">\n            </div>\n            <div class=\"form-group\">\n                <label for=\"cc-number\" class=\"control-label\">Credit Card Number</label>\n                <input id=\"cc-number\" type=\"tel\" class=\"input-lg form-control cc-number\" placeholder=\"•••• •••• •••• ••••\" required>\n            </div>\n\n            <div class=\"row form-group\">\n                <div class=\"col-xs-6\">\n                    <label for=\"cc-exp\" class=\"control-label\">Expiration Date</label>\n                    <input id=\"cc-exp\" type=\"tel\" class=\"input-lg form-control cc-exp\" placeholder=\"•• / ••\" required>\n                </div>\n                <div class=\"col-xs-6\">\n                    <label for=\"cc-cvc\" class=\"control-label\">CVC</label>\n                    <input id=\"cc-cvc\" type=\"tel\" class=\"input-lg form-control cc-cvc\" autocomplete=\"off\" placeholder=\"•••\" required>\n                </div>\n            </div>\n            <div class=\"row form-group\">\n                <div class=\"col-xs-6\">\n                    <button type=\"submit\" class=\"btn btn-lg btn-primary sb_btn sb_btn_fill\">Save Card</button>\n                </div>\n                <div class=\"col-xs-6\">\n                    <button id=\"js-cancel\" class=\"btn btn-lg btn-primary sb_btn sb_btn_remove sb_btn_fill\">Cancel</button>\n                </div>\n            </div>\n            <h2 class=\"validation\"></h2>\n        </form>\n    </div>\n</div>";
},"useData":true});
exports["comment_input"] = Handlebars.template({"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : {}, alias2=helpers.helperMissing, alias3="function", alias4=container.escapeExpression;

  return "<div class=\"input-group comment-input\"\n     data-type=\""
    + alias4(((helper = (helper = helpers.parent_type || (depth0 != null ? depth0.parent_type : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"parent_type","hash":{},"data":data}) : helper)))
    + "\"\n     data-id=\""
    + alias4(((helper = (helper = helpers.parent_id || (depth0 != null ? depth0.parent_id : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"parent_id","hash":{},"data":data}) : helper)))
    + "\">\n    <textarea class=\"input-group form-control\"\n              rows=\"2\" name=\"comment_content\"\n              placeholder=\""
    + alias4(((helper = (helper = helpers.placeholder_text || (depth0 != null ? depth0.placeholder_text : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"placeholder_text","hash":{},"data":data}) : helper)))
    + "\"></textarea>\n    <a class=\"btn input-group-btn comment-btn\"\n       data-id=\""
    + alias4(((helper = (helper = helpers.id || (depth0 != null ? depth0.id : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"id","hash":{},"data":data}) : helper)))
    + "\">\n        <span class=\"fa fa-plus\"></span>\n    </a>\n</div>";
},"useData":true});
exports["payment_info"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : {}, alias2=helpers.helperMissing, alias3="function", alias4=container.escapeExpression;

  return "                <li><label>Payment Method</label><i class=\"fa fa-credit-card\" style=\"padding-left: 5px;\"></i>\n                    "
    + alias4(((helper = (helper = helpers.brand || (depth0 != null ? depth0.brand : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"brand","hash":{},"data":data}) : helper)))
    + " **** **** **** "
    + alias4(((helper = (helper = helpers.dynamic_last4 || (depth0 != null ? depth0.dynamic_last4 : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"dynamic_last4","hash":{},"data":data}) : helper)))
    + " Expiration: "
    + alias4(((helper = (helper = helpers.exp_month || (depth0 != null ? depth0.exp_month : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"exp_month","hash":{},"data":data}) : helper)))
    + "/"
    + alias4(((helper = (helper = helpers.exp_year || (depth0 != null ? depth0.exp_year : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"exp_year","hash":{},"data":data}) : helper)))
    + "</li>\n";
},"3":function(container,depth0,helpers,partials,data) {
    return "Change Payment Method";
},"5":function(container,depth0,helpers,partials,data) {
    return "Add Payment Method";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : {}, alias2=helpers.helperMissing, alias3="function", alias4=container.escapeExpression;

  return "<div class=\"block\">\n    <h3 class=\"block-title\">Payment Information</h3>\n    <div class=\"block-content settings-list\">\n        <ul>\n"
    + ((stack1 = helpers["if"].call(alias1,(depth0 != null ? depth0.card_on_file : depth0),{"name":"if","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data})) != null ? stack1 : "")
    + "            <li><label>Next payment due:</label> "
    + alias4(((helper = (helper = helpers.next_due_date || (depth0 != null ? depth0.next_due_date : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"next_due_date","hash":{},"data":data}) : helper)))
    + "</li>\n            <li><label>Amount:</label> $"
    + alias4(((helper = (helper = helpers.bill_rate || (depth0 != null ? depth0.bill_rate : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"bill_rate","hash":{},"data":data}) : helper)))
    + "</li>\n        </ul>\n        <div class=\"row\">\n            <div class=\"col-lg-4 col-md-6 col-xs-12\">\n                <button class=\"btn btn-primary sb_btn sb_btn_fill\" id=\"js-payment-method\">\n                    "
    + ((stack1 = helpers["if"].call(alias1,(depth0 != null ? depth0.card_on_file : depth0),{"name":"if","hash":{},"fn":container.program(3, data, 0),"inverse":container.program(5, data, 0),"data":data})) != null ? stack1 : "")
    + "\n                </button>\n            </div>\n        </div>\n    </div>\n</div>";
},"useData":true});
exports["payment_methods"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, alias1=container.lambda, alias2=container.escapeExpression;

  return "                    <tr>\n                        <td>\n"
    + ((stack1 = helpers["if"].call(depth0 != null ? depth0 : {},(depth0 != null ? depth0["default"] : depth0),{"name":"if","hash":{},"fn":container.program(2, data, 0),"inverse":container.program(4, data, 0),"data":data})) != null ? stack1 : "")
    + "                            "
    + alias2(alias1((depth0 != null ? depth0.brand : depth0), depth0))
    + "\n                        </td>\n                        <td>\n                            "
    + alias2(alias1((depth0 != null ? depth0.last4 : depth0), depth0))
    + "\n                        </td>\n                        <td>\n                            "
    + alias2(alias1((depth0 != null ? depth0.exp_month : depth0), depth0))
    + "/"
    + alias2(alias1((depth0 != null ? depth0.exp_year : depth0), depth0))
    + "\n                        </td>\n                    </tr>\n";
},"2":function(container,depth0,helpers,partials,data) {
    var alias1=container.lambda, alias2=container.escapeExpression;

  return "                                <label class=\"radio\">\n                                    <input type=\"radio\" name=\"group1\" class=\"js-payment-method-option\"\n                                           value=\""
    + alias2(alias1((depth0 != null ? depth0.id : depth0), depth0))
    + "\"\n                                           id=\""
    + alias2(alias1((depth0 != null ? depth0.id : depth0), depth0))
    + "\"\n                                           data-toggle=\"radio\" checked>\n                                </label>\n";
},"4":function(container,depth0,helpers,partials,data) {
    var alias1=container.lambda, alias2=container.escapeExpression;

  return "                                <label class=\"radio\">\n                                    <input type=\"radio\" name=\"group1\" class=\"js-payment-method-option\"\n                                           value=\""
    + alias2(alias1((depth0 != null ? depth0.id : depth0), depth0))
    + "\"\n                                           id=\""
    + alias2(alias1((depth0 != null ? depth0.id : depth0), depth0))
    + "\"\n                                           data-toggle=\"radio\">\n                                </label>\n";
},"6":function(container,depth0,helpers,partials,data) {
    return "                    <tr>\n                        <td>\n                            Please add a payment method\n                        </td>\n                    </tr>\n";
},"8":function(container,depth0,helpers,partials,data) {
    var stack1;

  return ((stack1 = helpers["if"].call(depth0 != null ? depth0 : {},(depth0 != null ? depth0.submit_payment : depth0),{"name":"if","hash":{},"fn":container.program(9, data, 0),"inverse":container.noop,"data":data})) != null ? stack1 : "");
},"9":function(container,depth0,helpers,partials,data) {
    return "                    <button class=\"btn btn-primary btn-sm sb_btn\" id=\"js-use-payment-method\">Use This Payment Method</button>\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, alias1=depth0 != null ? depth0 : {};

  return "    <div class=\"block\">\n        <h3 class=\"block-title\">Payment Methods</h3>\n        <div class=\"block-content\">\n            <table class=\"table table-striped payment-methods\">\n                <tr>\n                    <th>\n                        Type\n                    </th>\n                    <th>\n                        Number\n                    </th>\n                    <th>\n                        Exp Date\n                    </th>\n                </tr>\n"
    + ((stack1 = helpers.each.call(alias1,(depth0 != null ? depth0.cards : depth0),{"name":"each","hash":{},"fn":container.program(1, data, 0),"inverse":container.program(6, data, 0),"data":data})) != null ? stack1 : "")
    + "            </table>\n"
    + ((stack1 = helpers["if"].call(alias1,(depth0 != null ? depth0.cards : depth0),{"name":"if","hash":{},"fn":container.program(8, data, 0),"inverse":container.noop,"data":data})) != null ? stack1 : "")
    + "            <button class=\"btn btn-primary btn-sm sb_btn\" id=\"js-add-payment-method\"><i class=\"fa fa-plus\"></i> Add Payment Method</button>\n        </div>\n    </div>";
},"useData":true});
exports["show_more_comments"] = Handlebars.template({"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : {}, alias2=helpers.helperMissing, alias3="function", alias4=container.escapeExpression;

  return "<div class=\"row\" id=\"additional-comment-wrapper-"
    + alias4(((helper = (helper = helpers.id || (depth0 != null ? depth0.id : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"id","hash":{},"data":data}) : helper)))
    + "\">\n    <div class=\"col-sm-5 col-sm-offset-1\">\n        <a href=\"javascript:;\" class=\"additional-comments\" id=\"additional-comments-"
    + alias4(((helper = (helper = helpers.id || (depth0 != null ? depth0.id : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"id","hash":{},"data":data}) : helper)))
    + "\">Show Older Comments ...</a>\n    </div>\n</div>";
},"useData":true});
exports["volunteer_table"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data) {
    var stack1;

  return "mailto:"
    + ((stack1 = helpers.each.call(depth0 != null ? depth0 : {},(depth0 != null ? depth0.volunteer : depth0),{"name":"each","hash":{},"fn":container.program(2, data, 0),"inverse":container.noop,"data":data})) != null ? stack1 : "");
},"2":function(container,depth0,helpers,partials,data) {
    return container.escapeExpression(container.lambda((depth0 != null ? depth0.email : depth0), depth0))
    + ",";
},"4":function(container,depth0,helpers,partials,data) {
    return "javascript:void(0);";
},"6":function(container,depth0,helpers,partials,data) {
    return "";
},"8":function(container,depth0,helpers,partials,data) {
    return "disabled";
},"10":function(container,depth0,helpers,partials,data) {
    var helper, alias1=container.lambda, alias2=container.escapeExpression;

  return "                    <tr>\n                        <td>\n                            "
    + alias2(alias1((depth0 != null ? depth0.first_name : depth0), depth0))
    + "\n                        </td>\n                        <td>\n                            "
    + alias2(alias1((depth0 != null ? depth0.last_name : depth0), depth0))
    + "\n                        </td>\n                        <td>\n                            <a class=\"sb-action-icon\" href=\"mailto:"
    + alias2(alias1((depth0 != null ? depth0.email : depth0), depth0))
    + "\"><i class=\"fa fa-envelope\"></i></a>\n                            <a class=\"sb-action-icon\" href=\""
    + alias2(((helper = (helper = helpers.profile || (depth0 != null ? depth0.profile : depth0)) != null ? helper : helpers.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : {},{"name":"profile","hash":{},"data":data}) : helper)))
    + "\"><i class=\"fa fa-user\"></i></a>\n                        </td>\n                    </tr>\n";
},"12":function(container,depth0,helpers,partials,data) {
    return "                    <tr>\n                        <td>\n                            No Current Volunteers\n                        </td>\n                    </tr>\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : {};

  return "    <div class=\"block\">\n        <div class=\"block block-type-title\">\n            <div class=\"block-content type-nav clearfix\">\n                <h1 >"
    + container.escapeExpression(((helper = (helper = helpers.block_name || (depth0 != null ? depth0.block_name : depth0)) != null ? helper : helpers.helperMissing),(typeof helper === "function" ? helper.call(alias1,{"name":"block_name","hash":{},"data":data}) : helper)))
    + "</h1>\n                <div class=\"title-important-actions\">\n                    <a class=\"btn btn-primary sb_btn\" href=\""
    + ((stack1 = helpers["if"].call(alias1,(depth0 != null ? depth0.volunteer : depth0),{"name":"if","hash":{},"fn":container.program(1, data, 0),"inverse":container.program(4, data, 0),"data":data})) != null ? stack1 : "")
    + "\" "
    + ((stack1 = helpers["if"].call(alias1,(depth0 != null ? depth0.volunteer : depth0),{"name":"if","hash":{},"fn":container.program(6, data, 0),"inverse":container.program(8, data, 0),"data":data})) != null ? stack1 : "")
    + ">Email All</a>\n                </div>\n            </div>\n        </div>\n\n        <div class=\"block-content\">\n            <table class=\"table table-striped payment-methods\">\n                <tr>\n                    <th>\n                        First Name\n                    </th>\n                    <th>\n                        Last Name\n                    </th>\n                    <th>\n                        Actions\n                    </th>\n                </tr>\n"
    + ((stack1 = helpers.each.call(alias1,(depth0 != null ? depth0.volunteer : depth0),{"name":"each","hash":{},"fn":container.program(10, data, 0),"inverse":container.program(12, data, 0),"data":data})) != null ? stack1 : "")
    + "            </table>\n        </div>\n    </div>\n";
},"useData":true});
exports["unverified_positions"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data) {
    var alias1=container.lambda, alias2=container.escapeExpression;

  return "            <tr>\n                <td>\n                    "
    + alias2(alias1((depth0 != null ? depth0.name : depth0), depth0))
    + "\n                </td>\n                <td class=\"position-created\">\n                    "
    + alias2(alias1((depth0 != null ? depth0.created : depth0), depth0))
    + "\n                </td>\n                <td>\n                    "
    + alias2(alias1((depth0 != null ? depth0.location_name : depth0), depth0))
    + "\n                </td>\n                <td>\n                    "
    + alias2(alias1((depth0 != null ? depth0.office_type : depth0), depth0))
    + "\n                </td>\n                <td>\n                    "
    + alias2(alias1((depth0 != null ? depth0.level : depth0), depth0))
    + "\n                </td>\n                <td>\n                    "
    + alias2(alias1((depth0 != null ? depth0.user_created : depth0), depth0))
    + "\n                </td>\n                <td>\n                    <a href=\"\"\n                       class=\"sb-action-icon js-verify-position\"\n                       data-object_uuid=\""
    + alias2(alias1((depth0 != null ? depth0.id : depth0), depth0))
    + "\"\n                       data-toggle=\"tooltip\"\n                       data-title=\"Verify Position\"\n                       data-placement=\"top\">\n                        <i class=\"fa fa-check\"></i>\n                    </a>\n                    <a href=\"/council/positions/"
    + alias2(alias1((depth0 != null ? depth0.id : depth0), depth0))
    + "/edit/\"\n                       class=\"js-edit-position\"\n                       data-object_uuid=\""
    + alias2(alias1((depth0 != null ? depth0.id : depth0), depth0))
    + "\"\n                       data-toggle=\"tooltip\"\n                       data-title=\"Edit Position\"\n                       data-placement=\"top\">\n                        <i class=\"fa fa-pencil-square-o\"></i>\n                    </a>\n                </td>\n            </tr>\n";
},"3":function(container,depth0,helpers,partials,data) {
    return "            <tr>\n                <td>\n                    No Current Unverified Positions\n                </td>\n            </tr>\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1;

  return "<div class=\"block-content\">\n    <table class=\"table table-striped payment-methods\">\n        <tbody><tr>\n            <th>\n                Position Name\n            </th>\n            <th>\n                Created\n            </th>\n            <th>\n                Location\n            </th>\n            <th>\n                Branch\n            </th>\n            <th>\n                Level\n            </th>\n            <th>\n                User Created\n            </th>\n            <th>\n                Actions\n            </th>\n        </tr>\n"
    + ((stack1 = helpers.each.call(depth0 != null ? depth0 : {},(depth0 != null ? depth0.positions : depth0),{"name":"each","hash":{},"fn":container.program(1, data, 0),"inverse":container.program(3, data, 0),"data":data})) != null ? stack1 : "")
    + "    </tbody></table>\n</div>";
},"useData":true});
exports["verified_positions"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data) {
    var alias1=container.lambda, alias2=container.escapeExpression;

  return "            <tr>\n                <td>\n                    "
    + alias2(alias1((depth0 != null ? depth0.name : depth0), depth0))
    + "\n                </td>\n                <td class=\"position-created\">\n                    "
    + alias2(alias1((depth0 != null ? depth0.created : depth0), depth0))
    + "\n                </td>\n                <td>\n                    "
    + alias2(alias1((depth0 != null ? depth0.location_name : depth0), depth0))
    + "\n                </td>\n                <td>\n                    "
    + alias2(alias1((depth0 != null ? depth0.office_type : depth0), depth0))
    + "\n                </td>\n                <td>\n                    "
    + alias2(alias1((depth0 != null ? depth0.level : depth0), depth0))
    + "\n                </td>\n                <td>\n                    "
    + alias2(alias1((depth0 != null ? depth0.user_created : depth0), depth0))
    + "\n                </td>\n                <td>\n                    <a href=\"\"\n                       class=\"sb-action-icon js-verify-position\"\n                       data-object_uuid=\""
    + alias2(alias1((depth0 != null ? depth0.id : depth0), depth0))
    + "\"\n                       data-toggle=\"tooltip\"\n                       data-title=\"Unverify Position\"\n                       data-placement=\"top\">\n                        <i class=\"fa fa-ban\"></i>\n                    </a>\n                </td>\n            </tr>\n";
},"3":function(container,depth0,helpers,partials,data) {
    return "            <tr>\n                <td>\n                    No Current Verified Positions\n                </td>\n            </tr>\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1;

  return "<div class=\"block-content\">\n    <table class=\"table table-striped payment-methods\">\n        <tbody><tr>\n            <th>\n                Position Name\n            </th>\n            <th>\n                Created\n            </th>\n            <th>\n                Location\n            </th>\n            <th>\n                Branch\n            </th>\n            <th>\n                Level\n            </th>\n            <th>\n                User Created\n            </th>\n            <th>\n                Actions\n            </th>\n        </tr>\n"
    + ((stack1 = helpers.each.call(depth0 != null ? depth0 : {},(depth0 != null ? depth0.positions : depth0),{"name":"each","hash":{},"fn":container.program(1, data, 0),"inverse":container.program(3, data, 0),"data":data})) != null ? stack1 : "")
    + "    </tbody></table>\n</div>";
},"useData":true});
exports["mission_search"] = Handlebars.template({"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : {}, alias2=helpers.helperMissing, alias3="function", alias4=container.escapeExpression;

  return "<div class=\"block search-block\">\n    <div class=\"row\">\n        <div class=\"col-xs-4 col-sm-3\">\n            <div class=\"thumbnail sb_thumbnail_md sb_thumbnail_search\">\n                <a href=\""
    + alias4(((helper = (helper = helpers.url || (depth0 != null ? depth0.url : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"url","hash":{},"data":data}) : helper)))
    + "\"><img src=\""
    + alias4(((helper = (helper = helpers.profile_pic || (depth0 != null ? depth0.profile_pic : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"profile_pic","hash":{},"data":data}) : helper)))
    + "\"></a>\n            </div>\n        </div>\n        <div class=\"col-xs-8 search-content-block\">\n            <h6><a href=\""
    + alias4(((helper = (helper = helpers.url || (depth0 != null ? depth0.url : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"url","hash":{},"data":data}) : helper)))
    + "\">"
    + alias4(((helper = (helper = helpers.title || (depth0 != null ? depth0.title : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"title","hash":{},"data":data}) : helper)))
    + "</a></h6>\n            <p>Started by: "
    + alias4(container.lambda(((stack1 = (depth0 != null ? depth0.quest : depth0)) != null ? stack1.title : stack1), depth0))
    + "</p>\n        </div>\n      </div>\n</div>";
},"useData":true});
exports["quest_search"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data) {
    var stack1, alias1=container.lambda, alias2=container.escapeExpression;

  return "                <p>"
    + alias2(alias1(((stack1 = (depth0 != null ? depth0.public_official : depth0)) != null ? stack1.state : stack1), depth0))
    + " - "
    + alias2(alias1(((stack1 = (depth0 != null ? depth0.public_official : depth0)) != null ? stack1.title : stack1), depth0))
    + "</p>\n";
},"3":function(container,depth0,helpers,partials,data) {
    var helper;

  return "                <p>"
    + container.escapeExpression(((helper = (helper = helpers.about || (depth0 != null ? depth0.about : depth0)) != null ? helper : helpers.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : {},{"name":"about","hash":{},"data":data}) : helper)))
    + "</p>\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : {}, alias2=helpers.helperMissing, alias3="function", alias4=container.escapeExpression;

  return "<div class=\"block search-block\">\n    <div class=\"row\">\n        <div class=\"col-xs-4 col-sm-3\">\n            <div class=\"thumbnail sb_thumbnail_md sb_thumbnail_search\">\n                <a href=\""
    + alias4(((helper = (helper = helpers.url || (depth0 != null ? depth0.url : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"url","hash":{},"data":data}) : helper)))
    + "\"><img src=\""
    + alias4(((helper = (helper = helpers.profile_pic || (depth0 != null ? depth0.profile_pic : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"profile_pic","hash":{},"data":data}) : helper)))
    + "\"></a>\n            </div>\n        </div>\n        <div class=\"col-xs-8 search-content-block\">\n            <h6><a href=\""
    + alias4(((helper = (helper = helpers.url || (depth0 != null ? depth0.url : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"url","hash":{},"data":data}) : helper)))
    + "\">"
    + alias4(((helper = (helper = helpers.title || (depth0 != null ? depth0.title : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"title","hash":{},"data":data}) : helper)))
    + " <i class=\"fa fa-rocket\"></i></a></h6>\n"
    + ((stack1 = helpers["if"].call(alias1,(depth0 != null ? depth0.public_official : depth0),{"name":"if","hash":{},"fn":container.program(1, data, 0),"inverse":container.program(3, data, 0),"data":data})) != null ? stack1 : "")
    + "        </div>\n      </div>\n</div>";
},"useData":true});
exports["question_search"] = Handlebars.template({"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : {}, alias2=helpers.helperMissing, alias3="function", alias4=container.escapeExpression;

  return "<div class=\"block search-block\">\n    <div class=\"row\">\n        <div class=\"col-xs-4 col-sm-3\">\n            <div class=\"search-vote-block\">\n                <h6>"
    + alias4(((helper = (helper = helpers.vote_count || (depth0 != null ? depth0.vote_count : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"vote_count","hash":{},"data":data}) : helper)))
    + " Votes</h6>\n                <h6>"
    + alias4(((helper = (helper = helpers.view_count || (depth0 != null ? depth0.view_count : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"view_count","hash":{},"data":data}) : helper)))
    + " Views</h6>\n            </div>\n        </div>\n        <div class=\"col-xs-8 search-content-block\">\n            <h6><a href=\""
    + alias4(((helper = (helper = helpers.url || (depth0 != null ? depth0.url : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"url","hash":{},"data":data}) : helper)))
    + "\">"
    + alias4(((helper = (helper = helpers.title || (depth0 != null ? depth0.title : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"title","hash":{},"data":data}) : helper)))
    + "</a></h6>\n            <p>"
    + alias4(((helper = (helper = helpers.first_name || (depth0 != null ? depth0.first_name : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"first_name","hash":{},"data":data}) : helper)))
    + " "
    + alias4(((helper = (helper = helpers.last_name || (depth0 != null ? depth0.last_name : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"last_name","hash":{},"data":data}) : helper)))
    + "</p>\n        </div>\n    </div>\n</div>";
},"useData":true});
exports["search_empty"] = Handlebars.template({"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<h3>Sorry! We couldn't find anything.</h3>";
},"useData":true});
exports["user_search"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data) {
    return "                <p>This is you :)</p>\n";
},"3":function(container,depth0,helpers,partials,data) {
    return "                <p>Reputation: --</p>\n";
},"5":function(container,depth0,helpers,partials,data) {
    var helper;

  return "                <p>Reputation: "
    + container.escapeExpression(((helper = (helper = helpers.reputation || (depth0 != null ? depth0.reputation : depth0)) != null ? helper : helpers.helperMissing),(typeof helper === "function" ? helper.call(depth0 != null ? depth0 : {},{"name":"reputation","hash":{},"data":data}) : helper)))
    + "</p>\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : {}, alias2=helpers.helperMissing, alias3="function", alias4=container.escapeExpression;

  return "<div class=\"block search-block\">\n    <div class=\"row\">\n        <div class=\"col-xs-4 col-sm-3\">\n            <div class=\"thumbnail sb_thumbnail_md sb_thumbnail_search\">\n              <a href=\""
    + alias4(((helper = (helper = helpers.url || (depth0 != null ? depth0.url : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"url","hash":{},"data":data}) : helper)))
    + "\"><img src=\""
    + alias4(((helper = (helper = helpers.profile_pic || (depth0 != null ? depth0.profile_pic : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"profile_pic","hash":{},"data":data}) : helper)))
    + "\"></a>\n            </div>\n        </div>\n        <div class=\"col-xs-8 search-content-block\">\n            <h6><a href=\""
    + alias4(((helper = (helper = helpers.url || (depth0 != null ? depth0.url : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"url","hash":{},"data":data}) : helper)))
    + "\">"
    + alias4(((helper = (helper = helpers.first_name || (depth0 != null ? depth0.first_name : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"first_name","hash":{},"data":data}) : helper)))
    + " "
    + alias4(((helper = (helper = helpers.last_name || (depth0 != null ? depth0.last_name : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"last_name","hash":{},"data":data}) : helper)))
    + "</a></h6>\n"
    + ((stack1 = (helpers.ifCond || (depth0 && depth0.ifCond) || alias2).call(alias1,(depth0 != null ? depth0.current_username : depth0),"==",(depth0 != null ? depth0.username : depth0),{"name":"ifCond","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data})) != null ? stack1 : "")
    + ((stack1 = (helpers.ifCond || (depth0 && depth0.ifCond) || alias2).call(alias1,(depth0 != null ? depth0.reputation : depth0),"==",0,{"name":"ifCond","hash":{},"fn":container.program(3, data, 0),"inverse":container.program(5, data, 0),"data":data})) != null ? stack1 : "")
    + "        </div>\n    </div>\n</div>";
},"useData":true});
exports["notifications"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data,blockParams,depths) {
    var stack1, alias1=depth0 != null ? depth0 : {};

  return "    <div class=\"block sb_notification_block\">\n        <div class=\"row notification-info\">\n            <div class=\"col-lg-2 col-md-2\">\n                <div class=\"thumbnail sb_thumbnail_sm\">\n"
    + ((stack1 = helpers["if"].call(alias1,(depth0 != null ? depth0.public_notification : depth0),{"name":"if","hash":{},"fn":container.program(2, data, 0, blockParams, depths),"inverse":container.program(4, data, 0, blockParams, depths),"data":data})) != null ? stack1 : "")
    + "                </div>\n            </div>\n            <div class=\"col-lg-10 col-md-10\">\n                <p class=\"sb_notification_link\">\n                    <a href=\""
    + container.escapeExpression(container.lambda((depth0 != null ? depth0.url : depth0), depth0))
    + "\" class=\"notification\">\n"
    + ((stack1 = helpers["if"].call(alias1,(depth0 != null ? depth0.public_notification : depth0),{"name":"if","hash":{},"fn":container.program(6, data, 0, blockParams, depths),"inverse":container.program(8, data, 0, blockParams, depths),"data":data})) != null ? stack1 : "")
    + "                    </a>\n                </p>\n            </div>\n        </div>\n    </div>\n";
},"2":function(container,depth0,helpers,partials,data,blockParams,depths) {
    var alias1=container.lambda, alias2=container.escapeExpression;

  return "                        <a href=\""
    + alias2(alias1((depth0 != null ? depth0.url : depth0), depth0))
    + "\" class=\"notification sb_notification_link\"><img src=\""
    + alias2(alias1((depths[1] != null ? depths[1].default_profile : depths[1]), depth0))
    + "\"></a>\n";
},"4":function(container,depth0,helpers,partials,data) {
    var stack1, alias1=container.lambda, alias2=container.escapeExpression;

  return "                        <a href=\""
    + alias2(alias1((depth0 != null ? depth0.url : depth0), depth0))
    + "\" class=\"notification sb_notification_link\"><img src=\""
    + alias2(alias1(((stack1 = (depth0 != null ? depth0.notification_from : depth0)) != null ? stack1.profile_pic : stack1), depth0))
    + "\"></a>\n";
},"6":function(container,depth0,helpers,partials,data) {
    var stack1;

  return "                            "
    + ((stack1 = container.lambda((depth0 != null ? depth0.action_name : depth0), depth0)) != null ? stack1 : "")
    + "\n";
},"8":function(container,depth0,helpers,partials,data) {
    var stack1, alias1=container.lambda, alias2=container.escapeExpression;

  return "                            "
    + alias2(alias1(((stack1 = (depth0 != null ? depth0.notification_from : depth0)) != null ? stack1.first_name : stack1), depth0))
    + " "
    + alias2(alias1(((stack1 = (depth0 != null ? depth0.notification_from : depth0)) != null ? stack1.last_name : stack1), depth0))
    + " "
    + ((stack1 = alias1((depth0 != null ? depth0.action_name : depth0), depth0)) != null ? stack1 : "")
    + "\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data,blockParams,depths) {
    var stack1;

  return ((stack1 = helpers.each.call(depth0 != null ? depth0 : {},(depth0 != null ? depth0.notifications : depth0),{"name":"each","hash":{},"fn":container.program(1, data, 0, blockParams, depths),"inverse":container.noop,"data":data})) != null ? stack1 : "");
},"useData":true,"useDepths":true});
exports["volunteer_selector"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data) {
    var alias1=container.lambda, alias2=container.escapeExpression;

  return "        <div class=\"registration-tooltip\">\n            <label class=\"checkbox\"\n                for=\""
    + alias2(alias1((depth0 != null ? depth0.value : depth0), depth0))
    + "\">\n                    "
    + alias2(alias1((depth0 != null ? depth0.display_name : depth0), depth0))
    + "\n                    <input type=\"checkbox\"\n                           value=\""
    + alias2(alias1((depth0 != null ? depth0.value : depth0), depth0))
    + "\"\n                           name=\"options\"\n                           id=\""
    + alias2(alias1((depth0 != null ? depth0.value : depth0), depth0))
    + "\"\n                           data-toggle=\"checkbox\">\n            </label>\n        </div>\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1;

  return "<div class=\"registration-tooltip\">\n    <label class=\"checkbox toggle-all\"\n        for=\"select_all\">\n            I'm Ready To Help With Everything!\n            <input type=\"checkbox\"\n                   value=\"\"\n                   name=\"select_all\"\n                   id=\"select_all\"\n                   data-toggle=\"checkbox\">\n    </label>\n</div>\n\n<div id=\"js-select-all\">\n"
    + ((stack1 = helpers.each.call(depth0 != null ? depth0 : {},(depth0 != null ? depth0.options : depth0),{"name":"each","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data})) != null ? stack1 : "")
    + "</div>";
},"useData":true});
exports["mission_list_block"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data) {
    var alias1=container.lambda, alias2=container.escapeExpression;

  return "<div class=\"block\">\n    <div class=\"row\">\n        <div class=\"col-xs-3\" style=\"padding-right: 0;\">\n            <div class=\"summary-block-img-wrapper\">\n                <img src=\""
    + alias2(alias1((depth0 != null ? depth0.wallpaper_pic : depth0), depth0))
    + "\">\n            </div>\n        </div>\n        <div class=\"col-xs-9\">\n            <h3 class=\"block-title\">\n                <a href=\""
    + alias2(alias1((depth0 != null ? depth0.url : depth0), depth0))
    + "\">"
    + alias2(alias1((depth0 != null ? depth0.title : depth0), depth0))
    + "</a>\n            </h3>\n            <div class=\"block-content\">\n                <small>"
    + alias2(alias1((depth0 != null ? depth0.about : depth0), depth0))
    + "</small>\n            </div>\n        </div>\n    </div>\n</div>\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1;

  return ((stack1 = helpers.each.call(depth0 != null ? depth0 : {},(depth0 != null ? depth0.missions : depth0),{"name":"each","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data})) != null ? stack1 : "");
},"useData":true});
exports["district_holder"] = Handlebars.template({"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    return "<label for=\"district-select\" hidden></label>\n<select id=\"district-select\" disabled class=\"form-control mission-input\">\n    <option selected disabled value=\"NaN\">Select a District</option>\n</select>\n";
},"useData":true});
exports["district_options"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data) {
    var alias1=container.lambda, alias2=container.escapeExpression;

  return "        <option value=\""
    + alias2(alias1((depth0 != null ? depth0.name : depth0), depth0))
    + "\">"
    + alias2(alias1((depth0 != null ? depth0.name : depth0), depth0))
    + "</option>\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1, helper, alias1=depth0 != null ? depth0 : {};

  return "<label for=\"district-select\" hidden></label>\n<select id=\"district-select\" class=\"form-control mission-input\">\n    <option selected disabled value=\"NaN\">"
    + container.escapeExpression(((helper = (helper = helpers.option_holder || (depth0 != null ? depth0.option_holder : depth0)) != null ? helper : helpers.helperMissing),(typeof helper === "function" ? helper.call(alias1,{"name":"option_holder","hash":{},"data":data}) : helper)))
    + "</option>\n"
    + ((stack1 = helpers.each.call(alias1,(depth0 != null ? depth0.districts : depth0),{"name":"each","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data})) != null ? stack1 : "")
    + "</select>\n";
},"useData":true});
exports["position_holder"] = Handlebars.template({"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var helper, alias1=depth0 != null ? depth0 : {}, alias2=helpers.helperMissing, alias3="function", alias4=container.escapeExpression;

  return "<div class=\"col-xs-12 col-sm-4\">\n    <div class=\"radio-image-selector-disabled\">\n        <div class=\"row radio-image-selector-image-wrapper\">\n            <img class=\"radio-image-selector-image\" src=\""
    + alias4(((helper = (helper = helpers.static_url || (depth0 != null ? depth0.static_url : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"static_url","hash":{},"data":data}) : helper)))
    + "images/executive_bw.png\">\n        </div>\n    </div>\n</div>\n<div class=\"col-xs-12 col-sm-4\">\n    <div class=\"radio-image-selector-disabled\">\n        <div class=\"row radio-image-selector-image-wrapper\">\n            <img class=\"radio-image-selector-image\" src=\""
    + alias4(((helper = (helper = helpers.static_url || (depth0 != null ? depth0.static_url : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"static_url","hash":{},"data":data}) : helper)))
    + "images/legislative_bw.png\">\n        </div>\n    </div>\n</div>\n<div class=\"col-xs-12 col-sm-4\">\n    <div class=\"radio-image-selector-disabled\">\n        <div class=\"row radio-image-selector-image-wrapper\">\n            <img class=\"radio-image-selector-image\" src=\""
    + alias4(((helper = (helper = helpers.static_url || (depth0 != null ? depth0.static_url : depth0)) != null ? helper : alias2),(typeof helper === alias3 ? helper.call(alias1,{"name":"static_url","hash":{},"data":data}) : helper)))
    + "images/judicial_bw.png\">\n        </div>\n    </div>\n</div>";
},"useData":true});
exports["position_image_radio"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data) {
    var alias1=container.lambda, alias2=container.escapeExpression;

  return "<div class=\"col-xs-12 col-sm-4\">\n    <div class=\"radio-image-selector js-position\" id=\""
    + alias2(alias1((depth0 != null ? depth0.name : depth0), depth0))
    + "\">\n        <h4 class=\"sb-profile-not-friend-header\">"
    + alias2(alias1((depth0 != null ? depth0.name : depth0), depth0))
    + "</h4>\n        <div class=\"row radio-image-selector-image-wrapper\">\n            <img class=\"radio-image-selector-image\" src=\""
    + alias2(alias1((depth0 != null ? depth0.image_path : depth0), depth0))
    + "\">\n        </div>\n    </div>\n</div>\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data) {
    var stack1;

  return ((stack1 = helpers.each.call(depth0 != null ? depth0 : {},(depth0 != null ? depth0.positions : depth0),{"name":"each","hash":{},"fn":container.program(1, data, 0),"inverse":container.noop,"data":data})) != null ? stack1 : "");
},"useData":true});
exports["mission_summary"] = Handlebars.template({"1":function(container,depth0,helpers,partials,data,blockParams,depths) {
    var alias1=container.lambda, alias2=container.escapeExpression;

  return "<div class=\"col-xs-12 col-sm-4\">\n    <div class=\"radio-image-selector js-position\" id=\""
    + alias2(alias1((depth0 != null ? depth0.id : depth0), depth0))
    + "\" data-slug=\""
    + alias2(alias1((depth0 != null ? depth0.slug : depth0), depth0))
    + "\">\n        <h4 class=\"sb-profile-not-friend-header\">"
    + alias2(alias1((depth0 != null ? depth0.title : depth0), depth0))
    + "</h4>\n        <div class=\"row radio-image-selector-image-wrapper\">\n            <img class=\"radio-image-selector-image\" src=\""
    + alias2(alias1((depths[1] != null ? depths[1].static_url : depths[1]), depth0))
    + "images/legislative_bw.png\">\n        </div>\n    </div>\n</div>\n";
},"compiler":[7,">= 4.0.0"],"main":function(container,depth0,helpers,partials,data,blockParams,depths) {
    var stack1;

  return ((stack1 = helpers.each.call(depth0 != null ? depth0 : {},(depth0 != null ? depth0.missions : depth0),{"name":"each","hash":{},"fn":container.program(1, data, 0, blockParams, depths),"inverse":container.noop,"data":data})) != null ? stack1 : "");
},"useData":true,"useDepths":true});