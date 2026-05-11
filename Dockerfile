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

# Copy all addons from your repository directly in one bulletproof line
COPY ./odoo/addons /mnt/extra-addons

# Ensure all files in /mnt/extra-addons are owned by the odoo system user
RUN chown -R odoo:odoo /mnt/extra-addons

# Switch back to the non-root odoo user
USER odoo

# Map Railway PG environment variables to Odoo's expected variables, 
# then launch Odoo with the official entrypoint, auto-selecting our database.
CMD ["sh", "-c", "export HOST=$PGHOST PORT=$PGPORT USER=$PGUSER PASSWORD=$PGPASSWORD; /entrypoint.sh odoo -d $PGDATABASE"]