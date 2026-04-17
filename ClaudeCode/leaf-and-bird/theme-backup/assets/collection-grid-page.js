/* 
 * Component: Collection Grid Page
 * Description: Advanced product grid with filtering, search, and sorting functionality
 */

// Global collection products data (previously inline script)
var collectionProducts = {
  'all': []
};

class CollectionGridPage {
  constructor(element) {
    this.element = element;
    this.sectionId = element.dataset.sectionId;
    
    // Cache DOM elements
    this.productCards = element.querySelectorAll('.product-card');
    this.collectionLinks = element.querySelectorAll('.collection-filter-link');
    this.sortSelect = element.querySelector('.sort-by-dropdown select');
    this.searchInput = element.querySelector('.product-search-input');
    this.searchClear = element.querySelector('.search-clear');
    this.sidebar = element.querySelector('.sidebar-filters');
    
    // Search state
    this.searchTimeout = null;
    
    this.init();
  }

  init() {
    this.initImageSliders();
    this.initColorSwatches();
    this.initCollectionFilters();
    this.initSorting();
    this.initSearch();
    this.initSidebarFilters();
    this.initFullCardClickable();
  }

  initImageSliders() {
    const sliders = this.element.querySelectorAll('.product-slider');
    
    sliders.forEach(slider => {
      const wrapper = slider.querySelector('.product-slider-wrapper');
      const slides = slider.querySelectorAll('.product-slide');
      const card = slider.closest('.product-card');
      const dots = card.querySelectorAll('.dot');
      
      if (slides.length <= 1) return;
      
      let currentSlide = 0;
      const slideCount = slides.length;
      
      this.updateDots(dots, currentSlide);
      
      // Touch swipe functionality
      let touchStartX = 0;
      let touchEndX = 0;
      
      slider.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
      }, {passive: true});
      
      slider.addEventListener('touchend', e => {
        touchEndX = e.changedTouches[0].screenX;
        this.handleSwipe(touchStartX, touchEndX, currentSlide, slideCount, wrapper, dots, (newSlide) => {
          currentSlide = newSlide;
        });
      }, {passive: true});
      
      // Mouse drag functionality
      this.initMouseDrag(slider, wrapper, dots, currentSlide, slideCount, (newSlide) => {
        currentSlide = newSlide;
      });
      
      // Connect dots to slides
      if (dots && dots.length) {
        dots.forEach((dot, i) => {
          dot.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            currentSlide = i;
            this.updateSlider(wrapper, currentSlide);
            this.updateDots(dots, currentSlide);
          });
        });
      }
    });
  }

  initMouseDrag(slider, wrapper, dots, currentSlide, slideCount, setCurrentSlide) {
    let isDragging = false;
    let startPosX = 0;
    
    slider.addEventListener('mousedown', e => {
      e.preventDefault();
      isDragging = true;
      startPosX = e.clientX;
      slider.style.cursor = 'grabbing';
    });
    
    slider.addEventListener('mousemove', e => {
      if (!isDragging) return;
      e.preventDefault();
      const moveX = e.clientX - startPosX;
      const slideWidth = slider.offsetWidth;
      
      if (Math.abs(moveX) < slideWidth * 0.5) {
        wrapper.style.transform = `translateX(${-currentSlide * 100 + (moveX / slideWidth * 100)}%)`;
      }
    });
    
    const handleMouseUp = (e) => {
      if (!isDragging) return;
      
      isDragging = false;
      slider.style.cursor = 'grab';
      
      const moveX = e.clientX - startPosX;
      const threshold = slider.offsetWidth * 0.2;
      
      if (moveX < -threshold) {
        currentSlide = Math.min(currentSlide + 1, slideCount - 1);
      } else if (moveX > threshold) {
        currentSlide = Math.max(currentSlide - 1, 0);
      }
      
      setCurrentSlide(currentSlide);
      this.updateSlider(wrapper, currentSlide);
      this.updateDots(dots, currentSlide);
    };
    
    document.addEventListener('mouseup', handleMouseUp);
    document.addEventListener('mouseleave', () => {
      if (isDragging) {
        isDragging = false;
        slider.style.cursor = 'grab';
        this.updateSlider(wrapper, currentSlide);
      }
    });
  }

  handleSwipe(startX, endX, currentSlide, slideCount, wrapper, dots, setCurrentSlide) {
    const threshold = 50;
    
    if (startX - endX > threshold) {
      currentSlide = Math.min(currentSlide + 1, slideCount - 1);
      setCurrentSlide(currentSlide);
      this.updateSlider(wrapper, currentSlide);
      this.updateDots(dots, currentSlide);
    } else if (endX - startX > threshold) {
      currentSlide = Math.max(currentSlide - 1, 0);
      setCurrentSlide(currentSlide);
      this.updateSlider(wrapper, currentSlide);
      this.updateDots(dots, currentSlide);
    }
  }

  updateSlider(wrapper, currentSlide) {
    wrapper.style.transform = `translateX(-${currentSlide * 100}%)`;
  }

  updateDots(dots, currentSlide) {
    if (dots && dots.length) {
      dots.forEach((dot, i) => {
        if (i === currentSlide) {
          dot.classList.add('active');
        } else {
          dot.classList.remove('active');
        }
      });
    }
  }

  initColorSwatches() {
    const swatches = this.element.querySelectorAll('.color-swatch');
    
    swatches.forEach(swatch => {
      swatch.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const productCard = swatch.closest('.product-card');
        const variantImage = swatch.getAttribute('data-variant-image');
        const cardSwatches = productCard.querySelectorAll('.color-swatch');
        
        // Remove active class from all swatches in this product
        cardSwatches.forEach(s => s.classList.remove('active'));
        
        // Add active class to clicked swatch
        swatch.classList.add('active');
        
        // Change product image if variant has an image
        if (variantImage && variantImage !== '') {
          const productImages = productCard.querySelectorAll('.product-image');
          if (productImages.length > 0) {
            productImages[0].src = variantImage;
          }
        }
      });
    });
  }

  initCollectionFilters() {
    // Handle initial state based on URL collection or active link
    const activeLink = this.element.querySelector('.collection-filter-link.active');
    if (activeLink) {
      const activeCollection = activeLink.getAttribute('data-collection');
      
      if (activeCollection === 'all') {
        // Show all products when "Shop All" is active
        this.productCards.forEach(card => {
          card.style.display = '';
        });
      } else if (activeCollection !== 'all') {
        // Filter products by specific collection
        this.productCards.forEach(card => {
          const cardCollections = card.getAttribute('data-collection') || '';
          if (cardCollections.includes(activeCollection)) {
            card.style.display = '';
          } else {
            card.style.display = 'none';
          }
        });
      }
    } else {
      // No active link, show all products
      this.productCards.forEach(card => {
        card.style.display = '';
      });
    }
    
    this.collectionLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remove active class from all links
        this.collectionLinks.forEach(l => l.classList.remove('active'));
        
        // Add active class to clicked link
        link.classList.add('active');
        
        const collectionHandle = link.getAttribute('data-collection');
        
        // Show/hide product cards based on collection
        this.productCards.forEach(card => {
          const cardCollections = card.getAttribute('data-collection') || '';
          
          let shouldShow = false;
          
          if (collectionHandle === 'all') {
            shouldShow = true;
          } else {
            shouldShow = cardCollections.includes(collectionHandle);
          }
          
          if (shouldShow) {
            card.style.display = '';
          } else {
            card.style.display = 'none';
          }
        });

        // Clear search when switching collections
        if (this.searchInput && this.searchInput.value.trim() !== '') {
          this.searchInput.value = '';
          if (this.searchClear) this.searchClear.style.display = 'none';
          this.element.classList.remove('searching');
        }
      });
    });
  }

  initSorting() {
    if (!this.sortSelect) return;
    
    this.sortSelect.addEventListener('change', () => {
      const selectedSort = this.sortSelect.value;
      const productGrid = this.element.querySelector('.product-grid');
      
      // Get only the visible products
      const visibleProducts = Array.from(this.productCards).filter(card => card.style.display !== 'none');
      
      // Sort products based on selection
      visibleProducts.sort((a, b) => {
        switch(selectedSort) {
          case 'price-ascending':
            return parseFloat(a.getAttribute('data-price')) - parseFloat(b.getAttribute('data-price'));
          case 'price-descending':
            return parseFloat(b.getAttribute('data-price')) - parseFloat(a.getAttribute('data-price'));
          case 'title-ascending':
            return a.getAttribute('data-title').localeCompare(b.getAttribute('data-title'));
          case 'title-descending':
            return b.getAttribute('data-title').localeCompare(a.getAttribute('data-title'));
          case 'created-ascending':
            return new Date(a.getAttribute('data-created')) - new Date(b.getAttribute('data-created'));
          case 'created-descending':
            return new Date(b.getAttribute('data-created')) - new Date(a.getAttribute('data-created'));
          default: // best-selling or default
            return parseInt(a.getAttribute('data-index')) - parseInt(b.getAttribute('data-index'));
        }
      });
      
      // Re-append sorted products to the grid
      visibleProducts.forEach(product => {
        productGrid.appendChild(product);
      });
    });
  }

  initSearch() {
    if (!this.searchInput) return;
    
    this.searchInput.addEventListener('input', (e) => {
      const searchTerm = e.target.value.toLowerCase().trim();
      
      // Show/hide clear button
      if (searchTerm.length > 0) {
        if (this.searchClear) this.searchClear.style.display = 'flex';
        this.element.classList.add('searching');
      } else {
        if (this.searchClear) this.searchClear.style.display = 'none';
        this.element.classList.remove('searching');
      }
      
      // Debounce search for better performance
      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        this.performSearch(searchTerm);
      }, 300);
    });
    
    // Clear search handler
    if (this.searchClear) {
      this.searchClear.addEventListener('click', () => {
        this.searchInput.value = '';
        this.searchClear.style.display = 'none';
        this.element.classList.remove('searching');
        this.showAllProducts();
      });
    }
  }

  performSearch(searchTerm) {
    if (searchTerm === '') {
      this.showAllProducts();
      return;
    }
    
    this.productCards.forEach(card => {
      const title = card.getAttribute('data-title')?.toLowerCase() || '';
      const vendor = card.getAttribute('data-vendor')?.toLowerCase() || '';
      const tags = card.getAttribute('data-tags')?.toLowerCase() || '';
      const type = card.getAttribute('data-type')?.toLowerCase() || '';
      
      // Search in title, vendor, tags, and type
      const isMatch = title.includes(searchTerm) || 
                     vendor.includes(searchTerm) || 
                     tags.includes(searchTerm) ||
                     type.includes(searchTerm);
      
      if (isMatch) {
        card.classList.remove('hidden');
        card.style.display = '';
      } else {
        card.classList.add('hidden');
        setTimeout(() => {
          if (card.classList.contains('hidden')) {
            card.style.display = 'none';
          }
        }, 300);
      }
    });
  }

  showAllProducts() {
    this.productCards.forEach(card => {
      card.classList.remove('hidden');
      card.style.display = '';
    });
  }

  initSidebarFilters() {
    if (!this.sidebar) return;
    
    const clearBtn = this.sidebar.querySelector('[data-clear-filters]');
    const inputs = this.sidebar.querySelectorAll('.sf-input');
    const header = this.sidebar.querySelector('.sidebar-filters__header');
    const content = this.sidebar.querySelector('.sidebar-filters__content');
    
    // Mobile dropdown functionality
    const initMobileDropdown = () => {
      if (window.innerWidth <= 767) {
        this.sidebar.classList.add('collapsed');
      } else {
        this.sidebar.classList.remove('collapsed');
      }
    };
    
    // Toggle dropdown on header click (mobile only)
    if (header) {
      header.addEventListener('click', (e) => {
        if (window.innerWidth <= 767) {
          if (!e.target.matches('.sidebar-filters__clear') && !e.target.closest('.sidebar-filters__clear')) {
            e.preventDefault();
            this.sidebar.classList.toggle('collapsed');
          }
        }
      });
    }
    
    // Initialize and handle resize
    initMobileDropdown();
    window.addEventListener('resize', initMobileDropdown);
    
    // Filter functionality
    const getActiveFilters = () => {
      const groups = {};
      inputs.forEach(input => {
        if (input.checked) {
          (groups[input.dataset.filterGroup] ||= []).push(input.value);
        }
      });
      return groups;
    };
    
    const matchesFilters = (card, groups) => {
      const vendor = this.normalize(card.dataset.vendor);
      const tags = (card.dataset.tags || '').toLowerCase();
      const title = this.normalize(card.dataset.title);
      const type = this.normalize(card.dataset.type);
      const cardCollections = card.getAttribute('data-collection') || '';

      for (const [group, values] of Object.entries(groups)) {
        if (!values.length) continue;
        const any = values.some(v => {
          const val = v.toLowerCase();
          
          if (group === 'collection') {
            if (val === 'all') {
              return true;
            } else {
              const collections = cardCollections.split(' ').filter(c => c.length > 0);
              return collections.includes(val);
            }
          } else if (group === 'size') {
            return title.includes(val) || tags.includes(val);
          } else if (group === 'color') {
            return title.includes(val) || tags.includes(val);
          } else if (group === 'material') {
            return title.includes(val) || tags.includes(val) || type.includes(val);
          } else if (group === 'style') {
            return title.includes(val) || tags.includes(val) || type.includes(val);
          } else {
            return vendor.includes(val) || tags.includes(val) || title.includes(val) || type.includes(val);
          }
        });
        if (!any) return false;
      }
      return true;
    };
    
    const applyFilters = () => {
      const groups = getActiveFilters();
      const hasFilters = Object.values(groups).some(arr => arr && arr.length);
      
      this.productCards.forEach(card => {
        if (!hasFilters || matchesFilters(card, groups)) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    };
    
    // Apply filters on button click
    const applyBtn = this.element.querySelector('[data-apply-filters]');
    if (applyBtn) {
      applyBtn.addEventListener('click', applyFilters);
    }
    
    // Clear filters
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        inputs.forEach(input => input.checked = false);
        applyFilters();
      });
    }
    
    // Initial filter application
    setTimeout(applyFilters, 40);
  }

  initFullCardClickable() {
    const clickableCards = this.element.querySelectorAll('.product-card.full-card-clickable');
    
    clickableCards.forEach(card => {
      const productUrl = card.getAttribute('data-product-url');
      if (!productUrl) return;
      
      let isSliding = false;
      let startX = 0;
      let startY = 0;
      const slideThreshold = 10;
      
      const handleStart = (e) => {
        isSliding = false;
        const touch = e.touches ? e.touches[0] : e;
        startX = touch.clientX;
        startY = touch.clientY;
      };
      
      const handleMove = (e) => {
        if (!startX || !startY) return;
        
        const touch = e.touches ? e.touches[0] : e;
        const deltaX = Math.abs(touch.clientX - startX);
        const deltaY = Math.abs(touch.clientY - startY);
        
        if (deltaX > slideThreshold || deltaY > slideThreshold) {
          isSliding = true;
        }
      };
      
      const handleCardClick = (e) => {
        if (isSliding) return;
        
        const clickedElement = e.target;
        if (clickedElement.closest('a, button, input, select, textarea')) {
          return;
        }
        
        if (clickedElement.closest('.product-dots, .dot')) {
          return;
        }
        
        window.location.href = productUrl;
      };
      
      // Add event listeners
      card.addEventListener('mousedown', handleStart);
      card.addEventListener('mousemove', handleMove);
      card.addEventListener('click', handleCardClick);
      
      card.addEventListener('touchstart', handleStart, { passive: true });
      card.addEventListener('touchmove', handleMove, { passive: true });
      
      card.addEventListener('touchend', () => {
        setTimeout(() => { isSliding = false; }, 100);
      }, { passive: true });
      
      card.addEventListener('mouseup', () => {
        setTimeout(() => { isSliding = false; }, 100);
      });
    });
  }

  normalize(str) {
    return (str || '').toString().toLowerCase().replace(/\s+/g, ' ').trim();
  }

  destroy() {
    // Clean up event listeners if needed
    clearTimeout(this.searchTimeout);
  }
}

// Auto-initialize components
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-component="collection-grid-page"]').forEach(element => {
    new CollectionGridPage(element);
  });
});

// Handle section reloads in theme editor
document.addEventListener('shopify:section:load', (event) => {
  const components = event.target.querySelectorAll('[data-component="collection-grid-page"]');
  components.forEach(element => {
    new CollectionGridPage(element);
  });
});
