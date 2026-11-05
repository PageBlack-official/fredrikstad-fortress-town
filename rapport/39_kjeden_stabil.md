# 39_kjeden_stabil: FEIL

kjeden feilet i kopien

Traceback (most recent call last):
  File "/tmp/kjede-l_axqi1q/repo/verktoy/bygg_kjede.py", line 17, in <module>
    import datalag, blanke_vegger  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/tmp/kjede-l_axqi1q/repo/verktoy/blanke_vegger.py", line 21, in <module>
    import datalag, vegger as VG, vinduer_regler as VR  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/tmp/kjede-l_axqi1q/repo/verktoy/vegger.py", line 8, in <module>
    from shapely.geometry import Polygon, LineString, Point
ModuleNotFoundError: No module named 'shapely'

