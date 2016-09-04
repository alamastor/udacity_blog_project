var applyHandlers = function() {
    'use strict';
    var comments = $('.comment');
    comments.each(function(idx) {
        var comment = $(comments[0]);
        var editButton = $(comment.find('.comment__edit--button'));
        var commentForm = $(comment.find('.comment__edit--form'));
        var cancelButton = comment.find('.comment__edit--cancel');
        commentForm.hide();

        editButton.click(function() {
            editButton.hide();
            commentForm.show();
        });

        cancelButton.click(function() {
            editButton.show();
            commentForm.hide();
        });
    });
};

$(applyHandlers());
