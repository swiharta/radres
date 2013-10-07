var Statuses = function() {
};
Statuses.prototype.add = function(options) {
    $.ajax({
               url: '/status',
               type: 'POST',
               dataType: 'json',
               data: { text: options.text },
               success: options.success
           });
};

var NewStatusView = function(options) {
    this.statuses = options.statuses;

    $('#new-status form').submit(this.addStatus);
//        var add = $.proxy(this.addStatus, this);
//        $('#new-status form').submit(add);
};
NewStatusView.prototype.addStatus = function(e) {
    e.preventDefault();
    console.log(this);
    this.statuses.add({
                          text: $('#new-status textarea').val(),
                          success: function(data) {
                              $('#statuses ul').append('<li>' + data.text + '</li>');
                              $('#new-status textarea').val('');
                          }
                      });
};

$(document).ready(function() {
    var statuses = new Statuses();
    new NewStatusView({ statuses: statuses });
});