import tensorflow as tf
import pickle


class CPM_Model(object):
    def __init__(self, total_num, input_size, heatmap_size, batch_size, stages, num_joints, img_type='RGB', is_training=True):    # is_trainng not be used
        self.stages = stages
        self.stage_heatmap = []
        self.stage_loss = [0] * stages
        self.total_loss = 0
        self.input_image = None
        self.center_map = None
        self.gt_heatmap = None
        self.learning_rate = 0
        self.merged_summary = None
        self.num_joints = num_joints
        self.inference_type = 'Train'
        self.batch_size_np = batch_size
        self.stage_loss_batch_hmindex = [0] * self.num_joints
        self.stage_loss_batch = [0] * self.batch_size_np
        self.total_num = total_num

        if img_type == 'RGB':
            self.input_images = tf.placeholder(dtype=tf.float32,
                                               shape=(None, input_size, input_size, 3),
                                               name='input_placeholder')
        elif img_type == 'GRAY':
            self.input_images = tf.placeholder(dtype=tf.float32,
                                               shape=(None, input_size, input_size, 1),
                                               name='input_placeholder')

        self.cmap_placeholder = tf.placeholder(dtype=tf.float32,
                                               shape=(None, input_size, input_size, 1),
                                               name='cmap_placeholder')

        self.gt_hmap_placeholder = tf.placeholder(dtype=tf.float32,
                                                  shape=(None, heatmap_size, heatmap_size, num_joints),
                                                  name='gt_hmap_placeholder')

        self.train_weights_placeholder = tf.placeholder(dtype=tf.float32,
                                                  shape=(None,num_joints),
                                                  name='train_weights_placeholder')
        self._build_model()

    def _build_model(self):
        with tf.variable_scope('pooled_center_map'):
            self.center_map = tf.layers.average_pooling2d(inputs=self.cmap_placeholder,
                                                          pool_size=[9, 9],
                                                          strides=[8, 8],
                                                          padding='same',
                                                          name='center_map')

        with tf.variable_scope('sub_stages'):
            sub_conv1 = tf.layers.conv2d(inputs=self.input_images,
                                         filters=64,
                                         kernel_size=[3, 3],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='sub_conv1')

            sub_conv2 = tf.layers.conv2d(inputs=sub_conv1,
                                         filters=64,
                                         kernel_size=[3, 3],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='sub_conv2')

            sub_pool1 = tf.layers.max_pooling2d(inputs=sub_conv2,
                                                pool_size=[2, 2],
                                                strides=2,
                                                padding='same',
                                                name='sub_pool1')

            sub_conv3 = tf.layers.conv2d(inputs=sub_pool1,
                                         filters=128,
                                         kernel_size=[3, 3],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='sub_conv3')

            sub_conv4 = tf.layers.conv2d(inputs=sub_conv3,
                                         filters=128,
                                         kernel_size=[3, 3],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='sub_conv4')

            sub_pool2 = tf.layers.max_pooling2d(inputs=sub_conv4,
                                                pool_size=[2, 2],
                                                strides=2,
                                                padding='same',
                                                name='sub_pool2')

            sub_conv5 = tf.layers.conv2d(inputs=sub_pool2,
                                         filters=256,
                                         kernel_size=[3, 3],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='sub_conv5')

            sub_conv6 = tf.layers.conv2d(inputs=sub_conv5,
                                         filters=256,
                                         kernel_size=[3, 3],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='sub_conv6')

            sub_conv7 = tf.layers.conv2d(inputs=sub_conv6,
                                         filters=256,
                                         kernel_size=[3, 3],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='sub_conv7')

            sub_conv8 = tf.layers.conv2d(inputs=sub_conv7,
                                         filters=256,
                                         kernel_size=[3, 3],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='sub_conv8')

            sub_pool3 = tf.layers.max_pooling2d(inputs=sub_conv8,
                                                pool_size=[2, 2],
                                                strides=2,
                                                padding='same',
                                                name='sub_pool3')

            sub_conv9 = tf.layers.conv2d(inputs=sub_pool3,
                                         filters=512,
                                         kernel_size=[3, 3],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='sub_conv9')

            sub_conv10 = tf.layers.conv2d(inputs=sub_conv9,
                                          filters=512,
                                          kernel_size=[3, 3],
                                          strides=[1, 1],
                                          padding='same',
                                          activation=tf.nn.relu,
                                          kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                          name='sub_conv10')

            sub_conv11 = tf.layers.conv2d(inputs=sub_conv10,
                                          filters=256,
                                          kernel_size=[3, 3],
                                          strides=[1, 1],
                                          padding='same',
                                          activation=tf.nn.relu,
                                          kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                          name='sub_conv11')

            sub_conv12 = tf.layers.conv2d(inputs=sub_conv11,
                                          filters=256,
                                          kernel_size=[3, 3],
                                          strides=[1, 1],
                                          padding='same',
                                          activation=tf.nn.relu,
                                          kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                          name='sub_conv12')

            sub_conv13 = tf.layers.conv2d(inputs=sub_conv12,
                                          filters=256,
                                          kernel_size=[3, 3],
                                          strides=[1, 1],
                                          padding='same',
                                          activation=tf.nn.relu,
                                          kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                          name='sub_conv13')

            sub_conv14 = tf.layers.conv2d(inputs=sub_conv13,
                                          filters=256,
                                          kernel_size=[3, 3],
                                          strides=[1, 1],
                                          padding='same',
                                          activation=tf.nn.relu,
                                          kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                          name='sub_conv14')

            self.sub_stage_img_feature = tf.layers.conv2d(inputs=sub_conv14,
                                                          filters=128,
                                                          kernel_size=[3, 3],
                                                          strides=[1, 1],
                                                          padding='same',
                                                          activation=tf.nn.relu,
                                                          kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                                          name='sub_stage_img_feature')

        with tf.variable_scope('stage_1'):
            conv1 = tf.layers.conv2d(inputs=self.sub_stage_img_feature,
                                     filters=512,
                                     kernel_size=[1, 1],
                                     strides=[1, 1],
                                     padding='same',
                                     activation=tf.nn.relu,
                                     kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                     name='conv1')

            self.stage_heatmap.append(tf.layers.conv2d(inputs=conv1,
                                                       filters=self.num_joints,
                                                       kernel_size=[1, 1],
                                                       strides=[1, 1],
                                                       padding='same',
                                                       kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                                       name='stage_heatmap'))

        for stage in range(2, self.stages + 1):
            self._middle_conv(stage)

    def _middle_conv(self, stage):
        with tf.variable_scope('stage_' + str(stage)):
            self.current_featuremap = tf.concat([self.stage_heatmap[stage - 2],
                                                 self.sub_stage_img_feature,
                                                 self.center_map,
                                                 ],
                                                axis=3)

            mid_conv1 = tf.layers.conv2d(inputs=self.current_featuremap,
                                         filters=128,
                                         kernel_size=[7, 7],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='mid_conv1')

            mid_conv2 = tf.layers.conv2d(inputs=mid_conv1,
                                         filters=128,
                                         kernel_size=[7, 7],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='mid_conv2')

            mid_conv3 = tf.layers.conv2d(inputs=mid_conv2,
                                         filters=128,
                                         kernel_size=[7, 7],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='mid_conv3')

            mid_conv4 = tf.layers.conv2d(inputs=mid_conv3,
                                         filters=128,
                                         kernel_size=[7, 7],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='mid_conv4')

            mid_conv5 = tf.layers.conv2d(inputs=mid_conv4,
                                         filters=128,
                                         kernel_size=[7, 7],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='mid_conv5')

            mid_conv6 = tf.layers.conv2d(inputs=mid_conv5,
                                         filters=128,
                                         kernel_size=[1, 1],
                                         strides=[1, 1],
                                         padding='same',
                                         activation=tf.nn.relu,
                                         kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                         name='mid_conv6')

            self.current_heatmap = tf.layers.conv2d(inputs=mid_conv6,
                                                    filters=self.num_joints,
                                                    kernel_size=[1, 1],
                                                    strides=[1, 1],
                                                    padding='same',
                                                    kernel_initializer=tf.contrib.layers.xavier_initializer(),
                                                    name='mid_conv7')

            self.stage_heatmap.append(self.current_heatmap)

    def build_loss(self, lr, lr_decay_rate, lr_decay_step, optimizer='Adam'):
        self.gt_heatmap = self.gt_hmap_placeholder
        self.total_loss = 0
        self.learning_rate = lr
        self.lr_decay_rate = lr_decay_rate
        self.lr_decay_step = lr_decay_step
        self.optimizer = optimizer
        self.batch_size = tf.cast(tf.shape(self.input_images)[0], dtype=tf.float32)

        for stage in range(self.stages):
            with tf.variable_scope('stage' + str(stage + 1) + '_loss'):
                self.stage_loss[stage] = tf.nn.l2_loss(self.stage_heatmap[stage] - self.gt_heatmap,
                                                       name='l2_loss') / self.batch_size
            tf.summary.scalar('stage' + str(stage + 1) + '_loss', self.stage_loss[stage])

        with tf.variable_scope('total_loss'):
            for stage in range(self.stages):
                self.total_loss += self.stage_loss[stage]
            tf.summary.scalar('total loss', self.total_loss)

        with tf.variable_scope('train'):
            self.global_step = tf.train.get_or_create_global_step()

            self.lr = tf.train.exponential_decay(self.learning_rate,
                                                 global_step=self.global_step,
                                                 decay_rate=self.lr_decay_rate,
                                                 decay_steps=self.lr_decay_step)
            tf.summary.scalar('learning rate', self.lr)

            self.train_op = tf.contrib.layers.optimize_loss(loss=self.total_loss,
                                                            global_step=self.global_step,
                                                            learning_rate=self.lr,
                                                            optimizer=self.optimizer)
        self.merged_summary = tf.summary.merge_all()

    # new learning rate setting method
    def build_loss2(self, optimizer='Adam'):
        self.gt_heatmap = self.gt_hmap_placeholder
        self.total_loss = 0
        self.optimizer = optimizer
        self.batch_size = tf.cast(tf.shape(self.input_images)[0], dtype=tf.float32)

        # 计算每个stage的loss
        for stage in range(self.stages):
            with tf.variable_scope('stage' + str(stage + 1) + '_loss'):
                self.stage_loss[stage] = tf.nn.l2_loss(self.stage_heatmap[stage] - self.gt_heatmap,
                                                       name='l2_loss') / self.batch_size
            tf.summary.scalar('stage' + str(stage + 1) + '_loss', self.stage_loss[stage])

        # 计算总loss
        with tf.variable_scope('total_loss'):
            for stage in range(self.stages):
                self.total_loss += self.stage_loss[stage]
            tf.summary.scalar('total loss', self.total_loss)

        with tf.variable_scope('train'):
            self.global_step = tf.train.get_or_create_global_step()

            # please set your own learning rate，decayed learning rate in build_loss() is also OK
            # new_lr =
            # self.lr = new_lr

            tf.summary.scalar('learning rate', self.lr)

            self.train_op = tf.contrib.layers.optimize_loss(loss=self.total_loss,
                                                            global_step=self.global_step,
                                                            learning_rate=self.lr,
                                                            optimizer=self.optimizer)
        self.merged_summary = tf.summary.merge_all()

    # new learning rate setting method
    def build_loss3(self, optimizer='Adam'):
        self.gt_heatmap = self.gt_hmap_placeholder
        self.train_weights = self.train_weights_placeholder
        self.total_loss = 0
        self.optimizer = optimizer
        self.batch_size = tf.cast(tf.shape(self.input_images)[0], dtype=tf.float32)

        # 计算每个stage的loss, weighted l2 loss
        for stage in range(self.stages):
            with tf.variable_scope('stage' + str(stage + 1) + '_loss'):
                self.stage_loss_batch = [0] * self.batch_size_np
                for batch in range(self.batch_size_np):
                    self.stage_loss_batch_hmindex = [0] * self.num_joints
                    for hmindex in range(self.num_joints):
                        self.stage_loss_batch_hmindex[hmindex] = tf.nn.l2_loss(self.stage_heatmap[stage][batch,:,:,hmindex] -
                                                      self.gt_heatmap[batch,:,:,hmindex]) * self.train_weights[batch][hmindex]
                    self.stage_loss_batch[batch] = tf.reduce_sum(self.stage_loss_batch_hmindex)
                self.stage_loss[stage] = tf.reduce_sum(self.stage_loss_batch) / self.batch_size
            tf.summary.scalar('stage' + str(stage + 1) + '_loss', self.stage_loss[stage])

        # 计算总loss
        with tf.variable_scope('total_loss'):
            for stage in range(self.stages):
                self.total_loss += self.stage_loss[stage]
            tf.summary.scalar('total loss', self.total_loss)

        with tf.variable_scope('train'):
            self.global_step = tf.train.get_or_create_global_step()

            step = tf.cast(self.global_step, dtype=tf.float64)

            ## Update Learning rate
            epcho = step * self.batch_size_np / self.total_num
            new_lr = tf.cond(tf.less(epcho, tf.constant(10.0, dtype=tf.float64)),
                             lambda: 0.0002 / 10.0 * epcho,
                             lambda: tf.cond(tf.less(epcho, tf.constant(20.0, dtype=tf.float64)),
                                     lambda: tf.constant(0.0002, dtype=tf.float64),
                                     lambda: tf.cond(tf.less(epcho, tf.constant(30.0, dtype=tf.float64)),
                                             lambda: 0.0002 - ((epcho - 20.0) / (30.0 - 20.0) * 0.00018),
                                             lambda: tf.constant(0.00002, dtype=tf.float64)
                                             )))
            self.lr = tf.cast(new_lr, tf.float32)

            tf.summary.scalar('learning rate', self.lr)

            self.train_op = tf.contrib.layers.optimize_loss(loss=self.total_loss,
                                                            global_step=self.global_step,
                                                            learning_rate=self.lr,
                                                            optimizer=self.optimizer)
        self.merged_summary = tf.summary.merge_all()

    def load_weights_from_file(self, weight_file_path, sess, finetune=True):
        weights = pickle.load(open(weight_file_path, 'rb'), encoding='latin1')

        with tf.variable_scope('', reuse=True):
            # Pre stage conv
            # conv1
            for layer in range(1, 3):
                conv_kernel = tf.get_variable('sub_stages/sub_conv' + str(layer) + '/kernel')
                conv_bias = tf.get_variable('sub_stages/sub_conv' + str(layer) + '/bias')

                loaded_kernel = weights['conv1_' + str(layer)]
                loaded_bias = weights['conv1_' + str(layer) + '_b']

                sess.run(tf.assign(conv_kernel, loaded_kernel))
                sess.run(tf.assign(conv_bias, loaded_bias))

            # conv2
            for layer in range(1, 3):
                conv_kernel = tf.get_variable('sub_stages/sub_conv' + str(layer + 2) + '/kernel')
                conv_bias = tf.get_variable('sub_stages/sub_conv' + str(layer + 2) + '/bias')

                loaded_kernel = weights['conv2_' + str(layer)]
                loaded_bias = weights['conv2_' + str(layer) + '_b']

                sess.run(tf.assign(conv_kernel, loaded_kernel))
                sess.run(tf.assign(conv_bias, loaded_bias))

            # conv3
            for layer in range(1, 5):
                conv_kernel = tf.get_variable('sub_stages/sub_conv' + str(layer + 4) + '/kernel')
                conv_bias = tf.get_variable('sub_stages/sub_conv' + str(layer + 4) + '/bias')

                loaded_kernel = weights['conv3_' + str(layer)]
                loaded_bias = weights['conv3_' + str(layer) + '_b']

                sess.run(tf.assign(conv_kernel, loaded_kernel))
                sess.run(tf.assign(conv_bias, loaded_bias))

            # conv4
            for layer in range(1, 3):
                conv_kernel = tf.get_variable('sub_stages/sub_conv' + str(layer + 8) + '/kernel')
                conv_bias = tf.get_variable('sub_stages/sub_conv' + str(layer + 8) + '/bias')

                loaded_kernel = weights['conv4_' + str(layer)]
                loaded_bias = weights['conv4_' + str(layer) + '_b']

                sess.run(tf.assign(conv_kernel, loaded_kernel))
                sess.run(tf.assign(conv_bias, loaded_bias))

            # conv4_CPM
            for layer in range(1, 5):
                conv_kernel = tf.get_variable('sub_stages/sub_conv' + str(layer + 10) + '/kernel')
                conv_bias = tf.get_variable('sub_stages/sub_conv' + str(layer + 10) + '/bias')

                loaded_kernel = weights['conv4_' + str(2 + layer) + '_CPM']
                loaded_bias = weights['conv4_' + str(2 + layer) + '_CPM_b']

                sess.run(tf.assign(conv_kernel, loaded_kernel))
                sess.run(tf.assign(conv_bias, loaded_bias))

            # conv5_3_CPM
            conv_kernel = tf.get_variable('sub_stages/sub_stage_img_feature/kernel')
            conv_bias = tf.get_variable('sub_stages/sub_stage_img_feature/bias')

            loaded_kernel = weights['conv4_7_CPM']
            loaded_bias = weights['conv4_7_CPM_b']

            sess.run(tf.assign(conv_kernel, loaded_kernel))
            sess.run(tf.assign(conv_bias, loaded_bias))

            # stage 1
            conv_kernel = tf.get_variable('stage_1/conv1/kernel')
            conv_bias = tf.get_variable('stage_1/conv1/bias')

            loaded_kernel = weights['conv5_1_CPM']
            loaded_bias = weights['conv5_1_CPM_b']

            sess.run(tf.assign(conv_kernel, loaded_kernel))
            sess.run(tf.assign(conv_bias, loaded_bias))

            if finetune != True:
                conv_kernel = tf.get_variable('stage_1/stage_heatmap/kernel')
                conv_bias = tf.get_variable('stage_1/stage_heatmap/bias')

                loaded_kernel = weights['conv5_2_CPM']
                loaded_bias = weights['conv5_2_CPM_b']

                sess.run(tf.assign(conv_kernel, loaded_kernel))
                sess.run(tf.assign(conv_bias, loaded_bias))

                # stage 2 and behind
                for stage in range(2, self.stages + 1):
                    for layer in range(1, 8):
                        conv_kernel = tf.get_variable('stage_' + str(stage) + '/mid_conv' + str(layer) + '/kernel')
                        conv_bias = tf.get_variable('stage_' + str(stage) + '/mid_conv' + str(layer) + '/bias')

                        loaded_kernel = weights['Mconv' + str(layer) + '_stage' + str(stage)]
                        loaded_bias = weights['Mconv' + str(layer) + '_stage' + str(stage) + '_b']

                        sess.run(tf.assign(conv_kernel, loaded_kernel))
                        sess.run(tf.assign(conv_bias, loaded_bias))
