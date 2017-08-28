import os
os.environ['GLOG_minloglevel'] = '2'
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import tensorflow as tf
import models
import numpy as np
import caffe
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check extracted TensorFlow model against Caffe model')
    parser.add_argument('--prototxt', type=str, default=os.path.join(os.path.dirname(__file__), '../tools/bvlc_alexnet.prototxt'),
                        help='path to the Caffe prototxt')
    parser.add_argument('--model', type=str, default=os.path.join(os.path.dirname(__file__), '../tools/bvlc_alexnet.caffemodel'),
                        help='path to the Caffe model')
    args = parser.parse_args()
    images = tf.placeholder(tf.float32, shape=[None, 227, 227, 3], name='images')
    training = tf.placeholder_with_default(True, shape=[], name='training')
    output, parameters = models.alexnet(images, training, pretrained=True)
    sess = tf.Session()
    init = tf.global_variables_initializer()
    data = np.random.rand(10, 227, 227, 3) * 4 + 150
    sess.run(init)
    result = sess.run(output, feed_dict={
        images: data,
        training: False
    })
    caffe_data = data.transpose(0, 3, 1, 2)[:, (2, 1, 0)]
    net = caffe.Net(args.prototxt, args.model, caffe.TEST)
    net.blobs['data'].reshape(*caffe_data.shape)
    net.blobs['data'].data[:] = caffe_data
    net.forward()
    diff = np.sum((result - net.blobs['fc8'].data) ** 2)
    if diff < 1e-5:
        print('Test Okay')
    else:
        print('Test failed')
        print('  diff: %f' % diff)