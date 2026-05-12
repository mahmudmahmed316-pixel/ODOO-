FROM odoo:18

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /mnt/extra-addons && chown -R odoo:odoo /mnt/extra-addons

COPY ./odoo_prod.conf /etc/odoo/odoo.conf
RUN chown odoo:odoo /etc/odoo/odoo.conf

COPY ./odoo/addons /mnt/extra-addons
RUN chown -R odoo:odoo /mnt/extra-addons

# Copy and set up the bulletproof entrypoint that cleans environment variables
# and correctly maps Railway's database variables to Odoo's expectations.
COPY ./run_odoo.py /run_odoo.py
RUN chmod +x /run_odoo.py

USER odoo

# Use our custom python script as the entrypoint.
ENTRYPOINT ["/run_odoo.py"]