/*
 * 
 * TableSorter pager companion
 * @requires jQuery v1.2.3
 * 
 * Copyright (c) 2007 Christian Bach
 * Copyright (c) 2008 Johan Euphrosine
 * Examples and docs at: http://tablesorter.com
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 * 
 */

(function($) {
	$.extend({
		tablesorterPager: new function() {
			function updatePageDisplay(table) {
			        var c = table.config;
				var s = $(c.cssPageDisplay,c.container).val((c.page+1) + c.seperator + c.totalPages);
				var pagelinks = $('.pagelinks', c.container).empty();;
				var range = c.computePageLinksRange(c.page+1, c.totalPages, c);
				if (c.totalPages == 1) {
				    c.container.hide();
				} else {
				    c.container.show();
				}
				for (var i = 0; i < range.page.length; ++i) {
				    (function() {
					var page = range.page[i];
					var label = range.label[i];
					var li = $('<li></li>').appendTo(pagelinks);
					var pagelink = $('<a href=\'javascript://\'></a>').appendTo(li).text(label).click(function() {c.page=page-1;moveToPage(table);});
					if (page == (c.page+1)) {
					    li.addClass('current');
					}
				    })();
				}
			}
			
			function setPageSize(table,size) {
			        var c = table.config;
				c.size = size;
				c.totalPages = Math.ceil(c.totalRows / c.size);
				c.pagerPositionSet = false;
				moveToPage(table);
				fixPosition(table);
			}
			
			function fixPosition(table) {
				var c = table.config;
				if(!c.pagerPositionSet && c.positionFixed) {
					var c = table.config, o = $(table);
					if(o.offset) {
						c.container.css({
							top: o.offset().top + o.height() + 'px',
							position: 'absolute'
						});
					}
					c.pagerPositionSet = true;
				}
			}
			
			function moveToFirstPage(table) {
				var c = table.config;
				c.page = 0;
				moveToPage(table);
			}
			
			function moveToLastPage(table) {
				var c = table.config;
				c.page = (c.totalPages-1);
				moveToPage(table);
			}
			
			function moveToNextPage(table) {
				var c = table.config;
				c.page++;
				if(c.page >= (c.totalPages-1)) {
					c.page = (c.totalPages-1);
				}
				moveToPage(table);
			}
			
			function moveToPrevPage(table) {
				var c = table.config;
				c.page--;
				if(c.page <= 0) {
					c.page = 0;
				}
				moveToPage(table);
			}
						
			
			function moveToPage(table) {
				var c = table.config;
				if(c.page < 0 || c.page > (c.totalPages-1)) {
					c.page = 0;
				}
				
				renderTable(table,c.rowsCopy);
			}
			
			function renderTable(table,rows) {
				
				var c = table.config;
				var l = rows.length;
				var s = (c.page * c.size);
				var e = (s + c.size);
				if(e > rows.length ) {
					e = rows.length;
				}
				
				
				var tableBody = $(table.tBodies[0]);
				
				// clear the table body
				
				$.tablesorter.clearTableBody(table);
				
				for(var i = s; i < e; i++) {
					
					//tableBody.append(rows[i]);
					
					var o = rows[i];
					var l = o.length;
					for(var j=0; j < l; j++) {
						
						tableBody[0].appendChild(o[j]);

					}
				}
				
				fixPosition(table,tableBody);
				
				$(table).trigger("applyWidgets");
				
				if( c.page >= c.totalPages ) {
        			moveToLastPage(table);
				}
				
				updatePageDisplay(table);
			}
			
			this.appender = function(table,rows) {
				
				var c = table.config;
				
				c.rowsCopy = rows;
				c.totalRows = rows.length;
				c.totalPages = Math.ceil(c.totalRows / c.size);
				
				renderTable(table,rows);
			};
			
			this.defaults = {
				size: 10,
				offset: 0,
				page: 0,
				totalRows: 0,
				totalPages: 0,
				container: null,
				cssNext: '.next',
				cssPrev: '.prev',
				cssFirst: '.first',
				cssLast: '.last',
				cssPageDisplay: '.pagedisplay',
				cssPageSize: '.pagesize',
				seperator: "/",
				positionFixed: true,
				appender: this.appender
			};

			this.defaults.computePageLinksRange = function(current, count, options) {
			    var size = 4;
			    var first = 1;
			    var last = count;
			    var left = current - size;
			    var right = current + size;
			    var page = [];
			    var label = [];
			    var opts = $.extend({}, options);
			    if (first == last) {
				return {label: [], page: []}
			    }
			    if (left < first) {
				left = 1;				
				right = Math.min(left + size + size, last);
			    }
			    if (right > last) {
				right = last;
				left = Math.max(right - size - size, first);
			    }
			    for (var i = left; i <= right; ++i) {
				page.push(i);
				label.push(i.toString());
			    }
			    if (left != 1) {
				page.unshift(first);
				var first_label = first.toString();
				if (first+1 < page[1]) {
				    first_label += '...';
				}
				label.unshift(first_label);
			    }
			    if (right != last) {		
				page.push(last);
				var last_label = last.toString();
				var end = page.length-1;
				if (page[end-1]+1 < last) {
				    last_label = '...' + last_label;
				}
				label.push(last_label);
			    }
			    if (opts.previous_label) {
				if (current > first) {
				    page.unshift(current - 1);
				    label.unshift(opts.previous_label);
				}
			    }
			    if (opts.next_label) {
				if (current < last) {
				    page.push(current + 1);
				    label.push(opts.next_label);
				}
			    }
			    return {page: page, label:label};
			};
			
			this.construct = function(settings) {
				
				return this.each(function() {	
					
					var config = $.extend(this.config, $.tablesorterPager.defaults, settings);
					
					var table = this, pager = config.container;
				
					config.size = parseInt($(".pagesize",pager).val());

					$(this).trigger("appendCache");
					
					$(config.cssFirst,pager).click(function() {
						moveToFirstPage(table);
						return false;
					});
					$(config.cssNext,pager).click(function() {
						moveToNextPage(table);
						return false;
					});
					$(config.cssPrev,pager).click(function() {
						moveToPrevPage(table);
						return false;
					});
					$(config.cssLast,pager).click(function() {
						moveToLastPage(table);
						return false;
					});
					$(config.cssPageSize,pager).change(function() {
						setPageSize(table,parseInt($(this).val()));
						return false;
					});
				});
			};
		}
	});
	// extend plugin scope
	$.fn.extend({
        tablesorterPager: $.tablesorterPager.construct
	});
	
})(jQuery);				