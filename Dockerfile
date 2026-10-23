FROM odoo:18.0

USER root

# Copy custom addons into Odoo's standard extra-addons directory
COPY ./custom_addons /mnt/extra-addons

# Fix ownership so Odoo user has full read/write access
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo

EXPOSE 8069 8072

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]
