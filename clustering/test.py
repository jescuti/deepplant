import model
import fiftyone as fo
import fiftyone.brain as fob

cluster = model.load_clustered_model("datasets")

images, scores = model.query_image("test-images/lycopodium.png", cluster, 4)

print(scores)