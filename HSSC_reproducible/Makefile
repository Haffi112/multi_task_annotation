# Reproduce every figure, table and number in the HSSC manuscript.
#   make all        both modes + sensitivity runs + numbers registry (about 6 minutes)
#   make revised    the manuscript version only
#   make inputs     rebuild/verify inputs from the private sources (authors only)
#   make osf        regenerate ../HSSC_osf_package from the revised outputs
PY := uv run python
SCRIPTS := src/10_human_validation.py src/11_descriptives.py src/12_temporal_trends.py \
           src/14_prevalence.py src/15_group_timelines.py src/16_gender_models.py

.PHONY: all reproduce revised sensitivity registry inputs osf clean

all: reproduce revised sensitivity registry

reproduce revised:
	@for s in $(SCRIPTS); do echo "== $$s --mode $@"; $(PY) $$s --mode $@ > logs/$$(basename $$s .py)_$@.log 2>&1 || { tail -20 logs/$$(basename $$s .py)_$@.log; exit 1; }; done

sensitivity:
	$(PY) src/15_group_timelines.py --mode sensitivity_distinct > logs/15_sensitivity_distinct.log 2>&1

registry:
	$(PY) src/91_check_reproduction.py > logs/91_check_reproduction.log 2>&1
	$(PY) src/90_numbers_registry.py > logs/90_numbers_registry.log 2>&1

inputs:
	$(PY) src/00_build_inputs.py

osf:
	$(PY) src/99_export_osf.py

clean:
	rm -rf outputs/reproduce outputs/revised outputs/sensitivity_distinct
