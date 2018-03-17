$(document).ready(function() {
  var SEARCH_LIMIT = 10;
  var SEARCH_DEBOUNCE_MS = 250;
  var searchOffset = 0;

  var $error = $('#error');
  var $nextPage = $('#next-page');
  var $previousPage = $('#previous-page');
  var $results = $('#results');
  var $search = $('#search');

  function displaySearchResults(results) {
    $error.addClass('hidden');

    if (!results || !results.length) {
      $('#results').text('No results were found :(');
      return;
    }

    var $resultsList = $('<ol />');
    $.each(results, function(i, result) {
      $('<li />')
      .appendTo($resultsList)
      .append($('<a />')
        .attr('href', Flask.url_for('document', { 'document_id': result }))
        .attr('target', '_blank')
        .text(result));
    });

    $results.html($resultsList.html());
  }

  function updatePaginationButtonState(numResults) {
    if (numResults === 0 && searchOffset > 0) {
      $nextPage.parent().addClass('disabled');
      $previousPage.parent().removeClass('disabled');
    } else if (numResults === 0 && searchOffset === 0) {
      $nextPage.parent().addClass('disabled');
      $previousPage.parent().addClass('disabled');
    } else if (numResults === SEARCH_LIMIT && searchOffset === 0) {
      $nextPage.parent().removeClass('disabled');
      $previousPage.parent().addClass('disabled');
    } else if (numResults === SEARCH_LIMIT && searchOffset > 0) {
      $nextPage.parent().removeClass('disabled');
      $previousPage.parent().removeClass('disabled');
    } else if (numResults < SEARCH_LIMIT && searchOffset === 0) {
      $nextPage.parent().addClass('disabled');
      $previousPage.parent().addClass('disabled');
    } else if (numResults < SEARCH_LIMIT && searchOffset > 0) {
      $nextPage.parent().addClass('disabled');
      $previousPage.parent().removeClass('disabled');
    } else {
      console.error('Unhandled page button state! numResults=' + numResults + ' searchOffset=' + searchOffset);
    }
  }

  function executeSearch(query) {
    if (!query || !query.length) {
      displaySearchResults([]);
      updatePaginationButtonState(0);
      return;
    }

    $.ajax({
      dataType: 'json',
      url: Flask.url_for('get_search_results', {
        'query': query,
        'offset': searchOffset,
        'limit': SEARCH_LIMIT
      }),
      success: function(response) {
        displaySearchResults(response.results);
        updatePaginationButtonState(response.results.length);
      },
      error: function(error) {
        console.error(error);
        $error.text('Error executing search.').removeClass('hidden');
      }
    });
  }

  $search.on('keyup input', $.debounce(SEARCH_DEBOUNCE_MS, function(e) {
    var query = e.target.value;
    searchOffset = 0;
    executeSearch(query);
  }));

  $previousPage.click(function() {
    var query = $search.val();
    searchOffset -= SEARCH_LIMIT;
    executeSearch(query);
  });

  $nextPage.click(function() {
    var query = $search.val();
    searchOffset += SEARCH_LIMIT;
    executeSearch(query);
  });

  var queryOnPageLoad = $search.val();
  if (queryOnPageLoad) {
    executeSearch(queryOnPageLoad);
  }
});
