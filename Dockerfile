FROM odoo:20.0

LABEL maintainer="Mouli Hotels & Resorts"
LABEL description="Odoo 20.0 with Hotel PMS, Resort Compliance, and Payroll modules"

USER root

# Ensure extra-addons directory exists and copy custom modules
RUN mkdir -p /mnt/extra-addons
COPY ./custom_addons /mnt/extra-addons

# Set correct ownership and permissions for the odoo user
RUN chown -R odoo:odoo /mnt/extra-addons \
    && chmod -R 755 /mnt/extra-addons

USER odoo

EXPOSE 8069 8072

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
