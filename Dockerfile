FROM odoo:18

# Switch to root to perform installations and permissions setup
USER root

# Install system dependencies if needed (e.g. git)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create directory for custom addons and set correct permissions
RUN mkdir -p /mnt/extra-addons && chown -R odoo:odoo /mnt/extra-addons

# Copy custom config file (using our verified production config)
COPY ./odoo_prod.conf /etc/odoo/odoo.conf
RUN chown odoo:odoo /etc/odoo/odoo.conf

# Copy custom addons individually (this enables high-speed Docker caching!)
COPY ./odoo/addons/base_account_budgethhhhh /mnt/extra-addons/base_account_budgethhhhh
COPY ./odoo/addons/base_accounting_kit /mnt/extra-addons/base_accounting_kit
COPY ./odoo/addons/community_premium_menu /mnt/extra-addons/community_premium_menu
COPY ./odoo/addons/community_studio_lite /mnt/extra-addons/community_studio_lite
COPY ./odoo/addons/custom_print /mnt/extra-addons/custom_print
COPY ./odoo/addons/customer_statement_extra /mnt/extra-addons/customer_statement_extra
COPY ./odoo/addons/partner_account_statement /mnt/extra-addons/partner_account_statement
COPY ./odoo/addons/pragtech_whatsapp_base /mnt/extra-addons/pragtech_whatsapp_base
COPY ./odoo/addons/query_deluxe /mnt/extra-addons/query_deluxe
COPY ./odoo/addons/quran_academys /mnt/extra-addons/quran_academys
COPY ./odoo/addons/stock_request /mnt/extra-addons/stock_request
COPY ./odoo/addons/stock_request_kanban /mnt/extra-addons/stock_request_kanban
COPY ./odoo/addons/stock_request_submit /mnt/extra-addons/stock_request_submit
COPY ./odoo/addons/synconics_bi_dashboard /mnt/extra-addons/synconics_bi_dashboard

# Ensure all custom addons are owned by the odoo system user
RUN chown -R odoo:odoo /mnt/extra-addons

# Switch back to the non-root odoo user
USER odoo

# Map Railway PG environment variables to Odoo's expected variables, 
# then launch Odoo with the official entrypoint, auto-selecting our database.
CMD ["sh", "-c", "export HOST=$PGHOST PORT=$PGPORT USER=$PGUSER PASSWORD=$PGPASSWORD; /entrypoint.sh odoo -d $PGDATABASE"]