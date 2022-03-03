# -*- coding: utf-8 -*-

"""
/***************************************************************************
 LineSplitter
                                 A QGIS plugin
 This plugin splits a line by points into many lines
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-02-23
        copyright            : (C) 2022 by Artsiom Sauchuk, CTLup
        email                : artsiom.sauchuk@uniroma1.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Artsiom Sauchuk, CTLup'
__date__ = '2022-02-23'
__copyright__ = '(C) 2022 by Artsiom Sauchuk, CTLup'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsVectorLayer,
                       QgsGeometry,
                       QgsFeature,
                       QgsField,
                       QgsFields,
                       QgsCoordinateTransformContext,
                       QgsVectorFileWriter,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from qgis import processing
from qgis.PyQt.QtCore import QVariant
import pdb

def from_point_list(points_features):
    for f in points_features:
        point = f.geometry().asPoint()

class LineSplitterAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT_1 = 'INPUT'
    INPUT_POINTS = 'INPUT_POINTS'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_1,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_POINTS,
                self.tr('Points layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(parameters, self.INPUT_1, context)
        points_splitter_layer = self.parameterAsSource(parameters, self.INPUT_POINTS, context)
        
        output_fields = QgsFields()
        output_fields.append(QgsField("sec_id", QVariant.Int))
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                context, output_fields, source.wkbType(), source.sourceCrs())
        
        
        line_point_layer = (processing.run(
            "native:extractvertices", 
            {
                'INPUT': '/home/artem/Work_general/ASTRAL_maps/csv/path.gpkg|layername=path', 
                'OUTPUT':'/home/artem/vertices.'
            },
            is_child_algorithm=True))['OUTPUT']
        pdb.set_trace()
        snapped_layer = (processing.run(
            "native:snapgeometries", 
            {
                'INPUT': points_splitter_layer.sourceName(), 
                'REFERENCE_LAYER': source.sourceName(), 
                'TOLERANCE': 100, 
                'BEHAVIOR': 1, 
                'OUTPUT':'TEMPORARY_OUTPUT'
            },
            context=context, 
            feedback=feedback, 
            is_child_algorithm=True))['OUTPUT']
        
        
        joined_layer = (processing.run(
            "native:joinbynearest",
            {
                'INPUT':line_point_layer,
                'INPUT_2':snapped_layer,
                'FIELDS_TO_COPY':['ord_ass'],
                'DISCARD_NONMATCHING':False,
                'PREFIX':'PATH_',
                'NEIGHBORS':2,
                'MAX_DISTANCE':None,
                'OUTPUT':'TEMPORARY_OUTPUT'
            },
            context=context, 
            feedback=feedback, 
            is_child_algorithm=True))['OUTPUT']


       
        line_point_layer = QgsVectorLayer(line_point_layer)
        joined_layer = QgsVectorLayer(joined_layer)
        pdb.set_trace()

        # ----------------------------------
        # path = "/home/artem/File.shp"    
        # options = QgsVectorFileWriter.SaveVectorOptions()
        # options.driverName = "ESRI Shapefile"

        # QgsVectorFileWriter.writeAsVectorFormatV2(line_point_layer, path, QgsCoordinateTransformContext(), options)
        # ----------------------------------

        
        # pdb.set_trace()
        line_point_features = line_point_layer.getFeatures()
        line_point_f_list = list()
        # sort line_point_features by ord_ass
        for feature in line_point_features:
            
            line_point_f_list.append(feature)
        line_point_f_list.sort(key=lambda f: int(f['ord_ass']))

        joined_d = dict()
        for feature in joined_layer.getFeatures():
            
            id = feature.id()
            if id not in joined_d or (id in joined_d and joined_d[id]["PATH_ord_ass"] > feature["PATH_ord_ass"]):
                joined_d[id] = feature

        invrt_joined = dict()       
    
        for f in joined_d.values():
            invrt_joined[f["PATH_ord_ass"]] = f
        merged_l = list()
        merged_l.append(list())
        for line_f in line_point_f_list:
            merged_l[-1].append(line_f)
            if line_f["ord_ass"] in invrt_joined:
                merged_l[-1].append(invrt_joined[line_f["ord_ass"]])
                merged_l.append(list())
                merged_l[-1].append(invrt_joined[line_f["ord_ass"]])

        for i, l in enumerate(merged_l):
            fet = QgsFeature(output_fields)
            fet.setAttribute('sec_id', i)
            fet.setGeometry(QgsGeometry.fromPolylineXY([f.geometry().asPoint() for f in l]))
            sink.addFeature(fet, QgsFeatureSink.FastInsert)
        # Compute the number of steps to display within the progress bar and
        # get features from source
        
        
        # total = 100.0 / source.featureCount() if source.featureCount() else 0
        # features = source.getFeatures()

        # for current, feature in enumerate(features):
        #     # Stop the algorithm if cancel button has been clicked
        #     if feedback.isCanceled():
        #         break

        #     # Add a feature in the sink
        #     sink.addFeature(feature, QgsFeatureSink.FastInsert)

        #     # Update the progress bar
        #     feedback.setProgress(int(current * total))


        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: dest_id}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Split a line by points'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return LineSplitterAlgorithm()
