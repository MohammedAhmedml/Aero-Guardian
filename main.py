import pathway as pw
from pipeline.ingestion import final_output

pw.debug.compute_and_print(final_output, include_id=False)

pw.run()
