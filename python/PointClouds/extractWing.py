# -*- coding: utf-8 -*-
# Euclidean Cluster Extraction
# http://pointclouds.org/documentation/tutorials/cluster_extraction.php#cluster-extraction
import numpy as np
import pcl

cloud = pcl.load('./pcd/out.pcd')

# downsampling of cloud

outrem = cloud.make_RadiusOutlierRemoval()
outrem.set_radius_search(1)
outrem.set_MinNeighborsInRadius(2)
cloud_outlierRemoved = outrem.filter ()

statRM = cloud.make_statistical_outlier_filter()
statRM.set_mean_k(50)
statRM.set_std_dev_mul_thresh(1.0)
cloud_clean = statRM.filter()

vg = cloud_clean.make_voxel_grid_filter()
vg.set_leaf_size (0.05, 0.05, 0.01)
cloud_filtered = vg.filter()
print("voxelized cloud has {} points".format(cloud_filtered.size))

# make segmenter object
#seg = cloud.make_segmenter()
#seg.set_optimize_coefficients (True)
#seg.set_model_type (pcl.SACMODEL_PLANE)
#seg.set_method_type (pcl.SAC_RANSAC)
#seg.set_MaxIterations (100)
#seg.set_distance_threshold (0.1)

# actual cluster segmentation
i = 0
nr_points = cloud_filtered.size
tree = cloud_filtered.make_kdtree()
ec = cloud_filtered.make_EuclideanClusterExtraction()
ec.set_ClusterTolerance (0.1)
ec.set_MinClusterSize (100)
ec.set_SearchMethod (tree)
cluster_indices = ec.Extract()

print('cluster_indices : ' + str(cluster_indices.count) + " count.")
cloud_cluster = pcl.PointCloud()

# output
for j, indices in enumerate(cluster_indices):
    print('indices = ' + str(len(indices)))
    points = np.zeros((len(indices), 3), dtype=np.float32)
    for i, indice in enumerate(indices):
        points[i][0] = cloud_filtered[indice][0]
        points[i][1] = cloud_filtered[indice][1]
        points[i][2] = cloud_filtered[indice][2]

    cloud_cluster.from_array(points)
    ss = "cloud_cluster_" + str(j) + ".pcd";
    pcl.save(cloud_cluster, ss)
