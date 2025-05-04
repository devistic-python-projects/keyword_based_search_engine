$(document).ready(function() {
    let timeout;
    $('#search-bar').on('input', function() {
        clearTimeout(timeout);
        const query = $(this).val();
        if (query) {
            timeout = setTimeout(() => {
                const words = query.split(/\s+/);
                let highlightedQuery = query;
                words.forEach(word => {
                    if (word.match(/^[a-zA-Z]+$/)) {
                        $.ajax({
                            url: '/spellcheck',
                            method: 'POST',
                            contentType: 'application/json',
                            data: JSON.stringify({ word: word }),
                            success: function(response) {
                                if (!response.is_correct) {
                                    highlightedQuery = highlightedQuery.replace(
                                        new RegExp(`\\b${word}\\b`, 'gi'),
                                        `<span class="misspelled" data-word="${word}" style="text-decoration: wavy red underline; cursor: pointer;">${word}</span>`
                                    );
                                    $('#search-bar').val(highlightedQuery);
                                }
                            }
                        });
                    }
                });
            }, 500);
        }
    });

    $(document).on('contextmenu', '.misspelled', function(e) {
        e.preventDefault();
        const word = $(this).data('word');
        $.ajax({
            url: '/spellcheck',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ word: word }),
            success: function(response) {
                const suggestions = response.suggestions || [];
                let html = suggestions.length
                    ? suggestions.map(s => `<li><a href="#" class="suggestion" data-word="${word}" data-suggestion="${s}">${s}</a></li>`).join('')
                    : '<li>No suggestions</li>';
                if (sessionStorage.getItem('user_id')) {
                    html += `<li><a href="#" class="add-to-dictionary" data-word="${word}">Add to dictionary</a></li>`;
                }
                $('#context-menu').html(html).css({
                    top: e.pageY,
                    left: e.pageX
                }).show();
            }
        });
    });

    $(document).on('click', '.suggestion', function(e) {
        e.preventDefault();
        const word = $(this).data('word');
        const suggestion = $(this).data('suggestion');
        const query = $('#search-bar').val();
        const newQuery = query.replace(
            new RegExp(`<span[^>]*>${word}</span>`, 'gi'),
            suggestion
        );
        $('#search-bar').val(newQuery);
        $('#context-menu').hide();
    });

    $(document).on('click', '.add-to-dictionary', function(e) {
        e.preventDefault();
        const word = $(this).data('word');
        $.ajax({
            url: '/add-to-dictionary',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ word: word }),
            success: function(response) {
                if (response.success) {
                    Swal.fire({
                        icon: 'success',
                        text: `Word "${word}" added to dictionary.`,
                        toast: true,
                        position: 'top-end',
                        showConfirmButton: false,
                        timer: 3000
                    });
                    const query = $('#search-bar').val();
                    const newQuery = query.replace(
                        new RegExp(`<span[^>]*>${word}</span>`, 'gi'),
                        word
                    );
                    $('#search-bar').val(newQuery);
                } else {
                    Swal.fire({
                        icon: 'error',
                        text: response.error || 'Failed to add word.',
                        toast: true,
                        position: 'top-end',
                        showConfirmButton: false,
                        timer: 3000
                    });
                }
            }
        });
        $('#context-menu').hide();
    });

    $(document).click(function(e) {
        if (!$(e.target).closest('.misspelled, #context-menu').length) {
            $('#context-menu').hide();
        }
    });
});

function showPreview(doc_id) {
    $.ajax({
        url: `/preview/${doc_id}`,
        method: 'GET',
        success: function(response) {
            if (response.error) {
                Swal.fire({
                    icon: 'error',
                    text: response.error,
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 3000
                });
            } else {
                Swal.fire({
                    title: response.filename,
                    text: response.content,
                    icon: 'info',
                    showConfirmButton: true,
                    width: '600px'
                });
            }
        },
        error: function() {
            Swal.fire({
                icon: 'error',
                text: 'Failed to load preview.',
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 3000
            });
        }
    });
}