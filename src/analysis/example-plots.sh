
# 10x10 pageload difference plot
python3 plots.py ../../data/postgres.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc-grid --pageload_diffs

# Pageload difference subset plots for each provider
python3 plots.py ../../data/postgres.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc --pageload_diffs_cf
python3 plots.py ../../data/postgres.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc --pageload_diffs_google
python3 plots.py ../../data/postgres.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc --pageload_diffs_quad9

# DNS timings
python3 plots.py ../../data/postgres.ini ../../data/tranco_combined.txt --matplotlibrc matplotlibrc --timing
