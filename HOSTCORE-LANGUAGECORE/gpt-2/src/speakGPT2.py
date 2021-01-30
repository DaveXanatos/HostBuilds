#!/usr/bin/env python3

import fire
import json
import os
import numpy as np
import tensorflow as tf
import zmq
import time
context = zmq.Context()

print("Connecting to Speech Center")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")   #5556 is visual, 5558 is language, 555$

import model, sample, encoder

def interact_model(
    model_name='345M', #345M on Pi4B4 or 8 only (memory allocation issue) 774 & 1558 too big for Pi4b8G too.
    seed=None,
    nsamples=1,
    batch_size=1,
    length=140,
    temperature=1.2,
    top_k=48,
    top_p=0.7,
    models_dir='models',
):

    models_dir = os.path.expanduser(os.path.expandvars(models_dir))
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0

    enc = encoder.get_encoder(model_name, models_dir)
    hparams = model.default_hparams()
    with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx // 2
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.Session(graph=tf.Graph()) as sess:
        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join(models_dir, model_name))
        saver.restore(sess, ckpt)

        while True:
            raw_text = input("\n\nModel prompt >>> ")
            while not raw_text:
                print('Prompt should not be empty!')
                raw_text = input("\n\nModel prompt >>> ")
            context_tokens = enc.encode(raw_text)
            generated = 0
            for _ in range(nsamples // batch_size):
                out = sess.run(output, feed_dict={
                    context: [context_tokens for _ in range(batch_size)]
                })[:, len(context_tokens):]
                for i in range(batch_size):
                    generated += 1
                    text = enc.decode(out[i])
                    stripFrag = text.rsplit(".", 1)
                    text = stripFrag[0] + "."  #Truncates after last "." to strip sent. frags.
                    print("=" * 40 + " SAMPLE " + str(generated) + " " + "=" * 40)
                    print(text)
                    socket.send_string(text)
                    message = socket.recv()
                    message = message.decode('utf-8')
                    if message==text:
                        print("1")
                    else:
                        print("0")
            print("=" * 80)

if __name__ == '__main__':
    fire.Fire(interact_model)

