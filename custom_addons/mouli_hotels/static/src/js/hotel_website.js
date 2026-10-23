/**
 * Mouli Hotels & RB Resorts - Interactive Website Room Booking & Real-time Calculator
 */

document.addEventListener("DOMContentLoaded", function () {
  // Real-time calculation on Room Detail Inquiry Form
  function setupLiveCalculator(formPrefix) {
    const cinInput = document.getElementById(formPrefix + "check_in");
    const coutInput = document.getElementById(formPrefix + "check_out");
    const rateInput = document.getElementById(formPrefix + "rate_val");
    const nightsEl = document.getElementById(formPrefix + "calc_nights");
    const totalEl = document.getElementById(formPrefix + "calc_total");

    if (!cinInput || !coutInput || !rateInput) return;

    function recalculate() {
      const cinVal = new Date(cinInput.value);
      const coutVal = new Date(coutInput.value);
      const rate = parseFloat(rateInput.value) || 0;

      if (cinVal && coutVal && coutVal > cinVal) {
        const diffTime = Math.abs(coutVal - cinVal);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        const nights = Math.max(1, diffDays);
        const total = nights * rate;

        if (nightsEl) nightsEl.textContent = nights + (nights === 1 ? " Night" : " Nights");
        if (totalEl) totalEl.textContent = "₹" + total.toLocaleString("en-IN");
      }
    }

    cinInput.addEventListener("change", function () {
      // Ensure checkout is at least 1 day after checkin
      const cinVal = new Date(cinInput.value);
      if (cinVal) {
        const nextDay = new Date(cinVal);
        nextDay.setDate(nextDay.getDate() + 1);
        const coutVal = new Date(coutInput.value);
        if (coutVal <= cinVal) {
          coutInput.value = nextDay.toISOString().split("T")[0];
        }
        coutInput.min = nextDay.toISOString().split("T")[0];
      }
      recalculate();
    });

    coutInput.addEventListener("change", recalculate);
    recalculate();
  }

  // Setup detail page calculator
  setupLiveCalculator("detail_");
  // Setup modal calculator
  setupLiveCalculator("modal_");

  // Quick Modal Room Selection Handler
  const quickBookBtns = document.querySelectorAll(".btn-quick-inquire");
  quickBookBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const roomTypeId = this.getAttribute("data-room-id");
      const roomTypeName = this.getAttribute("data-room-name");
      const roomRate = this.getAttribute("data-room-rate");

      const selectEl = document.getElementById("modal_room_type_id");
      if (selectEl && roomTypeId) {
        selectEl.value = roomTypeId;
      }

      const modalRateInput = document.getElementById("modal_rate_val");
      if (modalRateInput && roomRate) {
        modalRateInput.value = roomRate;
      }

      const modalTitleEl = document.getElementById("modal_selected_room_name");
      if (modalTitleEl && roomTypeName) {
        modalTitleEl.textContent = roomTypeName;
      }

      // Trigger recalculate
      const coutInput = document.getElementById("modal_check_out");
      if (coutInput) {
        coutInput.dispatchEvent(new Event("change"));
      }
    });
  });

  // Mobile Sticky CTA Smooth Scroll to Form
  const mobileBookNowLinks = document.querySelectorAll('a[href="#detailInquiryForm"]');
  mobileBookNowLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const targetForm = document.getElementById("detailInquiryForm");
      if (targetForm) {
        targetForm.scrollIntoView({ behavior: "smooth", block: "start" });
        const nameInput = targetForm.querySelector('input[name="guest_name"]');
        if (nameInput) {
          setTimeout(function () {
            nameInput.focus();
          }, 450);
        }
      }
    });
  });
});
