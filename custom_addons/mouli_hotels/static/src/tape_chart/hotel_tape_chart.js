/** @odoo-module **/

import { Component, proxy, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class HotelTapeChart extends Component {
    static template = "mouli_hotels.HotelTapeChart";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        const today = new Date().toISOString().split("T")[0];

        this.state = proxy({
            startDate: today,
            daysCount: 11,
            propertyId: null,
            mealPlan: "CP",
            selectedStatusFilter: "all",
            searchQuery: "",
            searchResults: [],
            searchResultsRoomIds: [],
            isSearching: false,
            showSearchResultsDropdown: false,
            highlightedBookingId: null,
            collapsedGroups: {},
            loading: true,
            data: null,
            showLegendModal: false,
            isFullscreen: false,

            // Quick Operations Side Drawer
            selectedBooking: null,
            showBookingDrawer: false,

            // Quick Booking Modal
            showQuickBookModal: false,
            quickBookForm: {
                guest_name: "",
                guest_phone: "",
                guest_email: "",
                property_id: null,
                room_id: null,
                room_type_id: null,
                check_in: today,
                check_out: "",
                nights: 1,
                adults: 1,
                children: 0,
                rate_per_night: 0,
                advance_payment: 0,
                advance_payment_method: "cash",
                notes: "",
                action_mode: "confirm",
            },
            guestSuggestions: [],

            // Room Quick Status Popover / Modal
            selectedRoomForStatus: null,
            showRoomStatusPopover: false,

            // Rich Tooltip
            hoveredBooking: null,
            tooltipPos: { x: 0, y: 0 },
        });

        onWillStart(async () => {
            await this.loadTapeChartData();
        });
    }

    async loadTapeChartData() {
        this.state.loading = true;
        try {
            const result = await this.orm.call(
                "hotel.reservation",
                "get_tape_chart_data",
                [],
                {
                    start_date_str: this.state.startDate,
                    days_count: this.state.daysCount,
                    property_id: this.state.propertyId,
                    meal_plan: this.state.mealPlan,
                }
            );
            this.state.data = result;
            if (!this.state.propertyId && result.current_property && result.current_property.id) {
                this.state.propertyId = result.current_property.id;
            }
        } catch (error) {
            console.error("Failed to load tape chart data:", error);
            this.notification.add("Could not load hotel reservation calendar data.", {
                type: "danger",
            });
        } finally {
            this.state.loading = false;
        }
    }

    // ==========================================
    // DATE & TIMELINE CONTROLS
    // ==========================================

    onDateChange(ev) {
        this.state.startDate = ev.target.value;
        this.loadTapeChartData();
    }

    onPrevDays(days = 7) {
        const d = new Date(this.state.startDate);
        d.setDate(d.getDate() - days);
        this.state.startDate = d.toISOString().split("T")[0];
        this.loadTapeChartData();
    }

    onNextDays(days = 7) {
        const d = new Date(this.state.startDate);
        d.setDate(d.getDate() + days);
        this.state.startDate = d.toISOString().split("T")[0];
        this.loadTapeChartData();
    }

    onToday() {
        this.state.startDate = new Date().toISOString().split("T")[0];
        this.loadTapeChartData();
    }

    setDaysCount(count) {
        if (this.state.daysCount === count) return;
        this.state.daysCount = count;
        this.loadTapeChartData();
    }

    getDateRangeLabel() {
        if (!this.state.data || !this.state.data.days_header || !this.state.data.days_header.length) {
            return "";
        }
        const headers = this.state.data.days_header;
        const first = headers[0];
        const last = headers[headers.length - 1];
        return `${first.day_number} ${first.month_name} – ${last.day_number} ${last.month_name}, ${new Date(this.state.startDate).getFullYear()} (${this.state.daysCount} Days)`;
    }

    // ==========================================
    // FILTERING & SEARCH
    // ==========================================

    onPropertyChange(ev) {
        this.state.propertyId = parseInt(ev.target.value, 10);
        this.loadTapeChartData();
    }

    onMealPlanChange(ev) {
        this.state.mealPlan = ev.target.value;
        this.loadTapeChartData();
    }

    onFilterStatus(status) {
        if (this.state.selectedStatusFilter === status) {
            this.state.selectedStatusFilter = "all";
        } else {
            this.state.selectedStatusFilter = status;
        }
    }

    clearFilter() {
        this.state.selectedStatusFilter = "all";
        this.clearSearch();
    }

    async onSearchInput(ev) {
        const val = ev.target.value;
        this.state.searchQuery = val;
        const query = val.trim();
        if (query.length >= 1) {
            this.state.isSearching = true;
            try {
                const results = await this.orm.call(
                    "hotel.reservation",
                    "search_tape_chart_guests",
                    [],
                    {
                        query: query,
                        property_id: this.state.propertyId,
                    }
                );
                this.state.searchResults = results || [];
                this.state.searchResultsRoomIds = (results || []).map((r) => r.room_id).filter(Boolean);
                this.state.showSearchResultsDropdown = true;
            } catch (err) {
                console.error("Guest search error:", err);
                this.state.searchResults = [];
                this.state.searchResultsRoomIds = [];
            } finally {
                this.state.isSearching = false;
            }
        } else {
            this.state.searchResults = [];
            this.state.searchResultsRoomIds = [];
            this.state.showSearchResultsDropdown = false;
            this.state.highlightedBookingId = null;
        }
    }

    closeSearchDropdown() {
        this.state.showSearchResultsDropdown = false;
    }

    onSearchFocus() {
        if (this.state.searchResults && this.state.searchResults.length) {
            this.state.showSearchResultsDropdown = true;
        }
    }

    clearSearch() {
        this.state.searchQuery = "";
        this.state.searchResults = [];
        this.state.searchResultsRoomIds = [];
        this.state.showSearchResultsDropdown = false;
        this.state.highlightedBookingId = null;
    }

    async onSelectSearchResult(item) {
        if (!item) return;
        this.state.showSearchResultsDropdown = false;
        this.state.highlightedBookingId = item.id;

        // Jump calendar directly to check-in date so stay is visible on the grid
        if (item.check_in) {
            this.state.startDate = item.check_in;
            await this.loadTapeChartData();
        }

        // Open quick drawer for this booking
        this.state.selectedBooking = item;
        this.state.showBookingDrawer = true;

        const statusLabel = item.state === "check_out" ? "Checked Out" : (item.state === "check_in" ? "In-House" : "Confirmed");
        this.notification.add(
            `Loaded stay for ${item.guest_name} (Room ${item.room_number}) [${statusLabel}]`,
            { type: "info" }
        );
    }

    toggleGroup(groupId) {
        this.state.collapsedGroups[groupId] = !this.state.collapsedGroups[groupId];
    }

    isGroupCollapsed(groupId) {
        return !!this.state.collapsedGroups[groupId];
    }

    toggleLegend() {
        this.state.showLegendModal = !this.state.showLegendModal;
    }

    toggleFullscreen() {
        const container = document.querySelector(".o_hotel_tape_chart_container");
        if (!document.fullscreenElement) {
            if (container && container.requestFullscreen) {
                container.requestFullscreen().catch(() => {});
                this.state.isFullscreen = true;
            } else if (container && container.webkitRequestFullscreen) {
                container.webkitRequestFullscreen();
                this.state.isFullscreen = true;
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen().catch(() => {});
                this.state.isFullscreen = false;
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
                this.state.isFullscreen = false;
            }
        }
    }

    // ==========================================
    // ROOM VISIBILITY & FILTERING
    // ==========================================

    isRoomVisible(room) {
        // Status filter check
        if (this.state.selectedStatusFilter === "vacant") {
            if (!(room.occupancy_status === "vacant" && room.maintenance_status === "operational")) {
                return false;
            }
        } else if (this.state.selectedStatusFilter === "occupied") {
            if (room.occupancy_status !== "occupied") return false;
        } else if (this.state.selectedStatusFilter === "reserved") {
            if (room.occupancy_status !== "reserved") return false;
        } else if (this.state.selectedStatusFilter === "blocked") {
            if (!(room.maintenance_status === "maintenance" || room.maintenance_status === "out_of_service")) {
                return false;
            }
        } else if (this.state.selectedStatusFilter === "dirty") {
            if (!(room.housekeeping_status === "dirty" || room.housekeeping_status === "cleaning")) {
                return false;
            }
        }

        // Live Search query check
        if (this.state.searchQuery) {
            const q = this.state.searchQuery.toLowerCase().trim();
            const matchesRoom = (room.number || "").toLowerCase().includes(q) ||
                                (room.name || "").toLowerCase().includes(q) ||
                                (room.floor || "").toLowerCase().includes(q);
            if (matchesRoom) return true;

            const matchesBooking = (room.bookings || []).some((b) =>
                (b.guest_name || "").toLowerCase().includes(q) ||
                (b.name || "").toLowerCase().includes(q) ||
                (b.guest_phone || "").toLowerCase().includes(q)
            );
            if (matchesBooking) return true;

            // Also keep room visible if this room has any reservation in global search results
            if (this.state.searchResultsRoomIds && this.state.searchResultsRoomIds.includes(room.id)) {
                return true;
            }

            return false;
        }

        return true;
    }

    getFilteredRooms(group) {
        return (group.rooms || []).filter((r) => this.isRoomVisible(r));
    }

    isReservationHighlighted(bk) {
        if (!bk) return false;
        if (this.state.highlightedBookingId && bk.id === this.state.highlightedBookingId) {
            return true;
        }
        if (!this.state.searchQuery) return false;
        const q = this.state.searchQuery.toLowerCase().trim();
        return (bk.guest_name || "").toLowerCase().includes(q) ||
               (bk.name || "").toLowerCase().includes(q) ||
               (bk.guest_phone || "").toLowerCase().includes(q);
    }

    // ==========================================
    // OPERATIONS: QUICK ACTION DRAWER (PMS STANDARD)
    // ==========================================

    onBookingClick(booking) {
        if (!booking) return;
        if (booking.status_style === "maintenance") {
            this.notification.add("This room is blocked for maintenance.", { type: "info" });
            return;
        }
        this.state.selectedBooking = booking;
        this.state.showBookingDrawer = true;
    }

    closeBookingDrawer() {
        this.state.showBookingDrawer = false;
        this.state.selectedBooking = null;
    }

    async doCheckIn(bookingId) {
        if (!bookingId) return;
        try {
            await this.orm.call("hotel.reservation", "action_check_in", [[bookingId]]);
            this.notification.add("Guest checked in successfully! Room is now In-House.", {
                type: "success",
            });
            this.closeBookingDrawer();
            await this.loadTapeChartData();
        } catch (error) {
            console.error("Check-in error:", error);
            this.notification.add("Failed to complete check-in. " + (error.message || ""), {
                type: "danger",
            });
        }
    }

    safeDoAction(action, options = {}) {
        if (!action) return;
        if (typeof action === "object" && action.type === "ir.actions.act_window") {
            if (!action.views || !Array.isArray(action.views) || action.views.length === 0) {
                const mode = action.view_mode ? action.view_mode.split(",")[0].trim() : "form";
                action.views = [[false, mode]];
            }
        }
        return this.action.doAction(action, options);
    }

    async doCheckOut(bookingId) {
        if (!bookingId) return;
        try {
            const actionRes = await this.orm.call("hotel.reservation", "action_check_out", [[bookingId]]);
            this.closeBookingDrawer();
            if (actionRes && typeof actionRes === "object" && actionRes.type) {
                // Opens quick settle & checkout wizard dialog
                await this.safeDoAction(actionRes, {
                    onClose: async () => {
                        await this.loadTapeChartData();
                    },
                });
            } else {
                this.notification.add("Guest checked out successfully! Housekeeping task scheduled.", {
                    type: "success",
                });
                await this.loadTapeChartData();
            }
        } catch (error) {
            console.error("Check-out error:", error);
            this.notification.add("Failed to complete checkout. " + (error.message || ""), {
                type: "danger",
            });
        }
    }

    async doViewFolio(resId) {
        if (!resId) return;
        try {
            const action = await this.orm.call("hotel.reservation", "action_view_folio", [[resId]]);
            if (action) {
                this.safeDoAction(action);
            }
        } catch (error) {
            console.error("Folio open error:", error);
            this.notification.add("Could not open folio.", { type: "danger" });
        }
    }

    async doPrintBill(resId) {
        if (!resId) return;
        try {
            const action = await this.orm.call("hotel.reservation", "action_print_bill", [[resId]]);
            if (action) {
                this.safeDoAction(action);
            }
        } catch (error) {
            console.error("Print bill error:", error);
            this.notification.add("Could not print bill.", { type: "danger" });
        }
    }

    doOpenFullReservation(resId) {
        if (!resId) return;
        this.safeDoAction({
            name: "Reservation Details",
            type: "ir.actions.act_window",
            res_model: "hotel.reservation",
            res_id: resId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    async doCancelReservation(resId) {
        if (!resId) return;
        if (!window.confirm("Are you sure you want to cancel this reservation? The assigned room will be freed.")) {
            return;
        }
        try {
            await this.orm.call("hotel.reservation", "action_cancel", [[resId]]);
            this.notification.add("Reservation has been cancelled.", { type: "warning" });
            this.closeBookingDrawer();
            await this.loadTapeChartData();
        } catch (error) {
            console.error("Cancel reservation error:", error);
            this.notification.add("Could not cancel reservation.", { type: "danger" });
        }
    }

    // ==========================================
    // OPERATIONS: QUICK BOOKING MODAL
    // ==========================================

    openQuickBook(room = null, day = null) {
        const todayStr = new Date().toISOString().split("T")[0];
        const checkInDate = day ? day.date : this.state.startDate || todayStr;
        
        const nextDay = new Date(checkInDate);
        nextDay.setDate(nextDay.getDate() + 1);
        const checkOutDate = nextDay.toISOString().split("T")[0];

        let roomId = null;
        let roomTypeId = null;
        let roomRate = 2000;

        if (room) {
            roomId = room.id;
            roomTypeId = room.room_type_id || (this.state.data?.all_room_types?.[0]?.id || null);
            roomRate = room.list_price || 2000;
        } else if (this.state.data && this.state.data.all_rooms_list && this.state.data.all_rooms_list.length) {
            const firstRoom = this.state.data.all_rooms_list[0];
            roomId = firstRoom.id;
            roomTypeId = firstRoom.room_type_id;
            roomRate = firstRoom.list_price || 2000;
        }

        this.state.quickBookForm = {
            guest_name: "",
            guest_phone: "",
            guest_email: "",
            property_id: this.state.propertyId,
            room_id: roomId,
            room_type_id: roomTypeId,
            check_in: checkInDate,
            check_out: checkOutDate,
            nights: 1,
            adults: 1,
            children: 0,
            rate_per_night: roomRate,
            advance_payment: 0,
            advance_payment_method: "cash",
            notes: "",
            action_mode: "confirm",
        };

        this.state.guestSuggestions = [];
        this.state.showQuickBookModal = true;
    }

    closeQuickBook() {
        this.state.showQuickBookModal = false;
    }

    onQuickBookRoomChange(ev) {
        const rId = parseInt(ev.target.value, 10);
        this.state.quickBookForm.room_id = rId;
        const found = (this.state.data.all_rooms_list || []).find((r) => r.id === rId);
        if (found) {
            this.state.quickBookForm.room_type_id = found.room_type_id;
            if (found.list_price) {
                this.state.quickBookForm.rate_per_night = found.list_price;
            }
        }
    }

    onQuickBookDatesChange() {
        const dIn = new Date(this.state.quickBookForm.check_in);
        const dOut = new Date(this.state.quickBookForm.check_out);
        if (dOut > dIn) {
            const diffDays = Math.ceil((dOut - dIn) / (1000 * 60 * 60 * 24));
            this.state.quickBookForm.nights = Math.max(1, diffDays);
        } else {
            this.state.quickBookForm.nights = 1;
        }
    }

    async onGuestNameInput(ev) {
        const val = ev.target.value;
        this.state.quickBookForm.guest_name = val;
        if (val.trim().length >= 2) {
            try {
                const results = await this.orm.call("hotel.reservation", "search_guests", [], {
                    query: val.trim(),
                });
                this.state.guestSuggestions = results || [];
            } catch {
                this.state.guestSuggestions = [];
            }
        } else {
            this.state.guestSuggestions = [];
        }
    }

    selectGuest(guest) {
        this.state.quickBookForm.guest_name = guest.name;
        if (guest.phone) this.state.quickBookForm.guest_phone = guest.phone;
        if (guest.email) this.state.quickBookForm.guest_email = guest.email;
        this.state.guestSuggestions = [];
    }

    async submitQuickBook(actionMode = "confirm") {
        const form = this.state.quickBookForm;
        if (!form.guest_name.trim()) {
            this.notification.add("Please enter a Guest Name.", { type: "warning" });
            return;
        }
        if (!form.room_id) {
            this.notification.add("Please select an Assigned Room.", { type: "warning" });
            return;
        }
        if (!form.check_in || !form.check_out) {
            this.notification.add("Please select Check-in and Check-out dates.", { type: "warning" });
            return;
        }

        form.action_mode = actionMode;

        this.state.loading = true;
        try {
            const result = await this.orm.call("hotel.reservation", "quick_create_reservation", [form]);
            const successMsg = actionMode === "check_in"
                ? `Reservation ${result.name} created and Guest checked in directly!`
                : `Reservation ${result.name} confirmed for ${result.guest_name}!`;
            this.notification.add(successMsg, { type: "success" });
            this.closeQuickBook();
            await this.loadTapeChartData();
        } catch (error) {
            console.error("Quick booking creation failed:", error);
            this.notification.add("Booking failed: " + (error.message || ""), { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    openFullFormBooking() {
        const form = this.state.quickBookForm;
        this.closeQuickBook();
        this.action.doAction({
            name: "New Hotel Reservation",
            type: "ir.actions.act_window",
            res_model: "hotel.reservation",
            views: [[false, "form"]],
            target: "current",
            context: {
                default_property_id: form.property_id || this.state.propertyId,
                default_room_id: form.room_id,
                default_room_type_id: form.room_type_id,
                default_check_in: `${form.check_in} 14:00:00`,
                default_check_out: `${form.check_out} 11:00:00`,
                default_adults: form.adults,
                default_children: form.children,
                default_rate_per_night: form.rate_per_night,
            },
        });
    }

    // ==========================================
    // OPERATIONS: ROOM HOUSEKEEPING & MAINTENANCE
    // ==========================================

    openRoomStatusModal(room) {
        this.state.selectedRoomForStatus = room;
        this.state.showRoomStatusPopover = true;
    }

    closeRoomStatusModal() {
        this.state.showRoomStatusPopover = false;
        this.state.selectedRoomForStatus = null;
    }

    async setRoomHousekeeping(room, status) {
        try {
            await this.orm.call("hotel.reservation", "quick_update_room_status", [room.id, "housekeeping", status]);
            room.housekeeping_status = status;
            this.notification.add(`Room ${room.number} marked as ${status.toUpperCase()}.`, { type: "success" });
            this.closeRoomStatusModal();
        } catch (error) {
            console.error("Room housekeeping update failed:", error);
            this.notification.add("Could not update room status.", { type: "danger" });
        }
    }

    async setRoomMaintenance(room, status) {
        try {
            await this.orm.call("hotel.reservation", "quick_update_room_status", [room.id, "maintenance", status]);
            room.maintenance_status = status;
            this.notification.add(`Room ${room.number} status set to ${status}.`, { type: "info" });
            this.closeRoomStatusModal();
            await this.loadTapeChartData();
        } catch (error) {
            console.error("Room maintenance update failed:", error);
            this.notification.add("Could not update room maintenance.", { type: "danger" });
        }
    }

    viewRoomForm(roomId) {
        if (!roomId) return;
        this.closeRoomStatusModal();
        this.action.doAction({
            name: "Room Setup",
            type: "ir.actions.act_window",
            res_model: "hotel.room",
            res_id: roomId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    // ==========================================
    // HOVER TOOLTIP
    // ==========================================

    onBookingMouseEnter(bk, ev) {
        if (bk.status_style === "maintenance") return;
        const rect = ev.currentTarget.getBoundingClientRect();
        this.state.hoveredBooking = bk;
        this.state.tooltipPos = {
            x: Math.min(window.innerWidth - 320, Math.max(10, rect.left)),
            y: rect.top - 120 > 10 ? rect.top - 120 : rect.bottom + 10,
        };
    }

    onBookingMouseLeave() {
        this.state.hoveredBooking = null;
    }
}

registry.category("actions").add("hotel_tape_chart", HotelTapeChart);

