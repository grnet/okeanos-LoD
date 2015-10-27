import Ember from 'ember';
import pagedArray from 'ember-cli-pagination/computed/paged-array';

export default Ember.ArrayController.extend({
  queryParams: ["page", "perPage"],

  page: 1,
  perPage: 10,
  firstOfCurrentPage: Ember.computed('page', 'perPage', function() {
    if(this.get('model.length') === 0) {
      return 0;
    }
    else {
      return (this.get('page')-1)*(this.get('perPage'))+1;
    }
  }),
  lastOfCurrentPage: Ember.computed('page', 'perPage', 'content', function() {
    return Math.min(this.get('content.length'), (this.get('page'))*(this.get('perPage')));
  }),

  pagedContent: pagedArray('content', {pageBinding: "page", perPageBinding: "perPage"}),

  totalPagesBinding: "pagedContent.totalPages",
});
